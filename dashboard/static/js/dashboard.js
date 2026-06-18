document.addEventListener('DOMContentLoaded', () => {
    // --- State Variables ---
    let socket;
    let selectedChartSymbol = 'EURUSD';
    let chart;
    const maxChartTicks = 20;
    const chartData = {
        EURUSD: [],
        GBPUSD: [],
        USDJPY: []
    };
    
    // Cache last prices to detect direction
    const lastPrices = {
        EURUSD: 0,
        GBPUSD: 0,
        USDJPY: 0
    };

    // --- Dom Elements ---
    const socketStatusDot = document.getElementById('socket-status-dot');
    const socketStatusText = document.getElementById('socket-status-text');
    
    // Forms
    const createUserForm = document.getElementById('create-user-form');
    const createAccountForm = document.getElementById('create-account-form');
    
    // Dropdowns
    const userSelect = document.getElementById('user-id-select');
    const syncAccountSelect = document.getElementById('sync-account-select');
    const calcAccountSelect = document.getElementById('calc-account-select');
    
    // Buttons
    const syncBtn = document.getElementById('btn-sync-trades');
    const calcBtn = document.getElementById('btn-calc-commissions');
    
    // Metrics
    const totalUsersVal = document.getElementById('stat-total-users');
    const totalAccountsVal = document.getElementById('stat-total-accounts');
    const totalTradesVal = document.getElementById('stat-total-trades');
    const totalCommissionsVal = document.getElementById('stat-total-commissions');

    // Chart Select
    const chartSymbolSelect = document.getElementById('chart-symbol-select');

    // --- Initialize Chart.js ---
    const ctx = document.getElementById('livePriceChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: selectedChartSymbol,
                data: [],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3,
                pointRadius: 3,
                pointBackgroundColor: '#8b5cf6'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748b', font: { size: 9 } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748b', font: { size: 10 } }
                }
            }
        }
    });

    // --- Socket.IO Setup ---
    function initSocket() {
        socket = io();

        socket.on('connect', () => {
            console.log('[Socket] Connected to server');
            socketStatusDot.classList.add('connected');
            socketStatusText.innerText = 'Connected';
            showToast('Socket Connected', 'Real-time WebSocket feed is active.', 'sync');

            // Subscribe to all symbol feeds
            socket.emit('subscribe', { symbols: ['EURUSD', 'GBPUSD', 'USDJPY'] }, (res) => {
                console.log('[Socket] Subscribed to symbol rooms:', res);
            });
        });

        socket.on('disconnect', () => {
            console.log('[Socket] Disconnected');
            socketStatusDot.classList.remove('connected');
            socketStatusText.innerText = 'Disconnected';
            showToast('Socket Disconnected', 'Lost connection to WebSocket server.', 'error');
        });

        // Listen for live prices
        socket.on('market_data', (data) => {
            const { symbol, price } = data;
            updateTickerUI(symbol, price);
            saveChartTick(symbol, price);
        });

        // Listen for live commissions
        socket.on('commission_created', (data) => {
            const { trade_id, commission } = data;
            showToast('Commission Processed', `Commission of $${commission.toFixed(2)} generated for Trade ID: ${trade_id}`, 'commission');
            // Refresh data dynamically
            refreshData();
        });
    }

    // --- Live Feed UI updates ---
    function updateTickerUI(symbol, price) {
        const priceEl = document.getElementById(`price-${symbol}`);
        if (!priceEl) return;

        const oldPrice = lastPrices[symbol] || 0;
        priceEl.innerText = price.toFixed(symbol === 'USDJPY' ? 2 : 4);

        // Remove old animation classes
        priceEl.classList.remove('price-up', 'price-down');

        if (oldPrice !== 0 && price > oldPrice) {
            priceEl.classList.add('price-up');
        } else if (oldPrice !== 0 && price < oldPrice) {
            priceEl.classList.add('price-down');
        }

        lastPrices[symbol] = price;
    }

    function saveChartTick(symbol, price) {
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const list = chartData[symbol];
        
        list.push({ time: timestamp, price: price });
        if (list.length > maxChartTicks) {
            list.shift();
        }

        // If the tick is for the currently selected chart symbol, update the chart
        if (symbol === selectedChartSymbol) {
            updateChart();
        }
    }

    function updateChart() {
        const dataList = chartData[selectedChartSymbol];
        chart.data.labels = dataList.map(d => d.time);
        chart.data.datasets[0].data = dataList.map(d => d.price);
        chart.data.datasets[0].label = selectedChartSymbol;
        
        // Custom color based on symbol
        if (selectedChartSymbol === 'EURUSD') {
            chart.data.datasets[0].borderColor = '#6366f1';
            chart.data.datasets[0].backgroundColor = 'rgba(99, 102, 241, 0.1)';
        } else if (selectedChartSymbol === 'GBPUSD') {
            chart.data.datasets[0].borderColor = '#10b981';
            chart.data.datasets[0].backgroundColor = 'rgba(16, 185, 129, 0.1)';
        } else {
            chart.data.datasets[0].borderColor = '#d946ef';
            chart.data.datasets[0].backgroundColor = 'rgba(217, 70, 239, 0.1)';
        }
        
        chart.update('none'); // Update without animation for smooth performance
    }

    // Chart symbol selection change
    chartSymbolSelect.addEventListener('change', (e) => {
        selectedChartSymbol = e.target.value;
        updateChart();
    });

    // --- API Calls & UI Populators ---

    // 1. Fetch Users
    async function fetchUsers() {
        try {
            const res = await fetch('/users');
            if (!res.ok) throw new Error('Failed to fetch users');
            const users = await res.json();
            
            // Populate Create Account select dropdown
            userSelect.innerHTML = '<option value="">-- Select a User --</option>';
            users.forEach(user => {
                const opt = document.createElement('option');
                opt.value = user.id;
                opt.innerText = `${user.name} (${user.email})`;
                userSelect.appendChild(opt);
            });

            // Populate Users Table
            const usersTbody = document.getElementById('users-tbody');
            if (users.length === 0) {
                usersTbody.innerHTML = `
                    <tr>
                        <td colspan="3" class="empty-state">
                            <i class="fa-regular fa-user"></i>
                            <p>No users registered yet.</p>
                        </td>
                    </tr>`;
            } else {
                usersTbody.innerHTML = '';
                users.forEach(u => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>#${u.id}</strong></td>
                        <td>${u.name}</td>
                        <td>${u.email}</td>
                    `;
                    usersTbody.appendChild(tr);
                });
            }

            return users.length;
        } catch (err) {
            console.error('Error fetching users:', err);
            return 0;
        }
    }

    // 2. Fetch Broker Accounts
    async function fetchAccounts() {
        try {
            const res = await fetch('/broker-accounts');
            if (!res.ok) throw new Error('Failed to fetch broker accounts');
            const accounts = await res.json();

            // Populate Sync and Calculate select dropdowns
            syncAccountSelect.innerHTML = '<option value="">-- Select Account --</option>';
            calcAccountSelect.innerHTML = '<option value="">-- Select Account --</option>';
            
            accounts.forEach(acc => {
                const text = `Acc #${acc.account_number} (Server: ${acc.server || 'Default'})`;
                
                const opt1 = document.createElement('option');
                opt1.value = acc.id;
                opt1.innerText = text;
                syncAccountSelect.appendChild(opt1);

                const opt2 = document.createElement('option');
                opt2.value = acc.id;
                opt2.innerText = text;
                calcAccountSelect.appendChild(opt2);
            });

            // Populate Accounts Table
            const accountsTbody = document.getElementById('accounts-tbody');
            if (accounts.length === 0) {
                accountsTbody.innerHTML = `
                    <tr>
                        <td colspan="4" class="empty-state">
                            <i class="fa-solid fa-wallet"></i>
                            <p>No broker accounts linked yet.</p>
                        </td>
                    </tr>`;
            } else {
                accountsTbody.innerHTML = '';
                accounts.forEach(a => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>#${a.id}</strong></td>
                        <td>User ID #${a.user_id}</td>
                        <td><span class="badge badge-info"><i class="fa-solid fa-server"></i> ${a.server}</span></td>
                        <td><code>${a.account_number}</code></td>
                    `;
                    accountsTbody.appendChild(tr);
                });
            }

            return accounts.length;
        } catch (err) {
            console.error('Error fetching accounts:', err);
            return 0;
        }
    }

    // 3. Fetch Trades
    async function fetchTrades() {
        try {
            const res = await fetch('/trades');
            if (!res.ok) throw new Error('Failed to fetch trades');
            const trades = await res.json();

            const tradesTbody = document.getElementById('trades-tbody');
            if (trades.length === 0) {
                tradesTbody.innerHTML = `
                    <tr>
                        <td colspan="7" class="empty-state">
                            <i class="fa-solid fa-arrow-right-arrow-left"></i>
                            <p>No trades synced yet. Sync some trades to calculate commissions.</p>
                        </td>
                    </tr>`;
            } else {
                tradesTbody.innerHTML = '';
                trades.forEach(t => {
                    const profitClass = t.profit >= 0 ? 'text-success' : 'text-danger';
                    const isClosed = t.close_time !== null;
                    const commissionText = t.commission_amount !== null ? 
                        `<span class="badge badge-success">$${t.commission_amount.toFixed(2)}</span>` : 
                        `<span class="badge badge-secondary">Pending</span>`;
                        
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>#${t.ticket}</strong></td>
                        <td>Acc #${t.account_id}</td>
                        <td>${t.symbol}</td>
                        <td>${t.volume.toFixed(2)}</td>
                        <td class="${profitClass}">$${t.profit.toFixed(2)}</td>
                        <td>
                            ${isClosed ? 
                                `<span class="badge badge-info"><i class="fa-solid fa-lock"></i> Closed</span>` : 
                                `<span class="badge badge-warning"><i class="fa-solid fa-spinner spinner"></i> Open</span>`}
                        </td>
                        <td>${commissionText}</td>
                    `;
                    tradesTbody.appendChild(tr);
                });
            }

            return trades;
        } catch (err) {
            console.error('Error fetching trades:', err);
            return [];
        }
    }

    // 4. Fetch Commissions
    async function fetchCommissions() {
        try {
            const res = await fetch('/commissions');
            if (!res.ok) throw new Error('Failed to fetch commissions');
            const commissions = await res.json();

            const commTbody = document.getElementById('commissions-tbody');
            if (commissions.length === 0) {
                commTbody.innerHTML = `
                    <tr>
                        <td colspan="5" class="empty-state">
                            <i class="fa-solid fa-dollar-sign"></i>
                            <p>No commissions calculated yet.</p>
                        </td>
                    </tr>`;
            } else {
                commTbody.innerHTML = '';
                commissions.forEach(c => {
                    const timeString = new Date(c.created_at + 'Z').toLocaleString();
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>#${c.id}</strong></td>
                        <td>Trade #${c.trade_id} (Ticket: ${c.ticket || 'N/A'})</td>
                        <td>${c.symbol || 'N/A'}</td>
                        <td>${c.volume !== undefined ? c.volume.toFixed(2) : 'N/A'}</td>
                        <td><span class="badge badge-success">$${c.commission_amount.toFixed(2)}</span></td>
                    `;
                    commTbody.appendChild(tr);
                });
            }

            return commissions;
        } catch (err) {
            console.error('Error fetching commissions:', err);
            return [];
        }
    }

    // Refresh All Data and Stats
    async function refreshData() {
        const uCount = await fetchUsers();
        const aCount = await fetchAccounts();
        const trades = await fetchTrades();
        const commissions = await fetchCommissions();

        // Update top-level Stats
        totalUsersVal.innerText = uCount;
        totalAccountsVal.innerText = aCount;
        totalTradesVal.innerText = trades.length;

        const sumCommissions = commissions.reduce((sum, c) => sum + c.commission_amount, 0);
        totalCommissionsVal.innerText = `$${sumCommissions.toFixed(2)}`;
    }

    // --- Form Submissions ---

    // Create User Form
    createUserForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('user-name').value;
        const email = document.getElementById('user-email').value;

        try {
            const res = await fetch('/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email })
            });
            const data = await res.json();

            if (res.ok) {
                showToast('User Created', `Successfully registered ${name}!`, 'sync');
                createUserForm.reset();
                refreshData();
            } else {
                throw new Error(data.error || 'Failed to create user');
            }
        } catch (err) {
            showToast('Error', err.message, 'error');
        }
    });

    // Link Broker Account Form
    createAccountForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const user_id = userSelect.value;
        const account_number = document.getElementById('acc-number').value;
        const server = document.getElementById('acc-server').value;
        const password = document.getElementById('acc-password').value;

        if (!user_id) {
            showToast('Validation Error', 'Please select a registered user.', 'error');
            return;
        }

        try {
            const res = await fetch('/broker-accounts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: parseInt(user_id), account_number, server, password })
            });
            const data = await res.json();

            if (res.ok) {
                showToast('Broker Account Added', `Account #${account_number} has been linked.`, 'sync');
                createAccountForm.reset();
                refreshData();
            } else {
                throw new Error(data.error || 'Failed to create broker account');
            }
        } catch (err) {
            showToast('Error', err.message, 'error');
        }
    });

    // Sync Trades Action
    syncBtn.addEventListener('click', async () => {
        const account_id = syncAccountSelect.value;
        if (!account_id) {
            showToast('Validation Error', 'Please select a broker account to sync.', 'error');
            return;
        }

        // UI Feedback
        syncBtn.disabled = true;
        const origHtml = syncBtn.innerHTML;
        syncBtn.innerHTML = '<i class="fa-solid fa-spinner spinner"></i> Syncing...';

        try {
            const res = await fetch(`/sync-trades/${account_id}`, { method: 'POST' });
            const data = await res.json();

            if (res.ok) {
                showToast('Synchronization Completed', `Successfully synced ${data.synced_trades} new trades from MT5.`, 'sync');
                refreshData();
            } else {
                throw new Error(data.error || 'Synchronization failed');
            }
        } catch (err) {
            showToast('Sync Failed', `Connection error: ${err.message}`, 'error');
        } finally {
            syncBtn.disabled = false;
            syncBtn.innerHTML = origHtml;
        }
    });

    // Calculate Commissions Action
    calcBtn.addEventListener('click', async () => {
        const account_id = calcAccountSelect.value;
        if (!account_id) {
            showToast('Validation Error', 'Please select a broker account to process.', 'error');
            return;
        }

        calcBtn.disabled = true;
        const origHtml = calcBtn.innerHTML;
        calcBtn.innerHTML = '<i class="fa-solid fa-spinner spinner"></i> Calculating...';

        try {
            const res = await fetch(`/calculate-commission/${account_id}`, { method: 'POST' });
            const data = await res.json();

            if (res.ok) {
                showToast('Calculation Finished', `Processed ${data.commissions_created} new commissions.`, 'sync');
                refreshData();
            } else {
                throw new Error(data.error || 'Calculation failed');
            }
        } catch (err) {
            showToast('Calculation Failed', `Error: ${err.message}`, 'error');
        } finally {
            calcBtn.disabled = false;
            calcBtn.innerHTML = origHtml;
        }
    });

    // --- Tab Switching Logic ---
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            
            tabButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(`tab-${targetTab}`).classList.add('active');
        });
    });

    // --- Toast Notifications System ---
    const toastContainer = document.getElementById('toast-container');

    window.showToast = function(title, body, type = 'sync') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let iconHtml = '<i class="fa-solid fa-circle-info toast-icon"></i>';
        if (type === 'commission') {
            iconHtml = '<i class="fa-solid fa-circle-check toast-icon"></i>';
        } else if (type === 'error') {
            iconHtml = '<i class="fa-solid fa-triangle-exclamation toast-icon"></i>';
        } else if (type === 'sync') {
            iconHtml = '<i class="fa-solid fa-rotate toast-icon"></i>';
        }

        toast.innerHTML = `
            ${iconHtml}
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-body">${body}</div>
            </div>
            <button class="toast-close">&times;</button>
        `;

        toastContainer.appendChild(toast);
        
        // Trigger entrance slide animation
        setTimeout(() => toast.classList.add('show'), 50);

        // Auto remove after 5 seconds
        const autoClose = setTimeout(() => {
            closeToast(toast);
        }, 5000);

        // Close on button click
        toast.querySelector('.toast-close').addEventListener('click', () => {
            clearTimeout(autoClose);
            closeToast(toast);
        });
    };

    function closeToast(toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 400);
    }

    // --- Startup ---
    initSocket();
    refreshData();
});
