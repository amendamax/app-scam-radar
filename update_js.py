import re

with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

new_script = """
        let currentPage = 1;
        let currentSearch = '';
        const limit = 50;

        async function loadData() {
            try {
                const response = await fetch(`/api/v1/apps?search=${currentSearch}&page=${currentPage}&limit=${limit}`);
                const data = await response.json();
                
                const tbody = document.getElementById('table-body');
                let html = '';
                
                if (data.results.length === 0) {
                    html = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No malicious apps found matching your search.</td></tr>`;
                } else {
                    data.results.forEach(item => {
                        let badgeClass = 'badge-adware';
                        let threatLower = item.threat_type.toLowerCase();
                        if(threatLower.includes('trojan') || threatLower.includes('drainer') || threatLower.includes('ransomware')) badgeClass = 'badge-trojan';
                        if(threatLower.includes('spyware') || threatLower.includes('keylogger')) badgeClass = 'badge-spyware';
                        
                        let icon = '<i class="fa-brands fa-android"></i>';
                        let platformLower = item.platform.toLowerCase();
                        if(platformLower.includes('play')) icon = '<i class="fa-brands fa-google-play"></i>';
                        if(platformLower.includes('store') || platformLower.includes('ios')) icon = '<i class="fa-brands fa-apple"></i>';
                        
                        let statusHtml = item.status.toLowerCase().includes('active')
                            ? `<span class="status status-active"><i class="fa-solid fa-circle-exclamation"></i> LIVE DANGER</span>`
                            : `<span class="status status-removed"><i class="fa-solid fa-circle-check"></i> REMOVED</span>`;

                        html += `
                        <tr class="table-row">
                            <td>
                                <div class="app-name"><i class="fa-solid fa-mobile-button"></i> ${item.app_name}</div>
                                <div class="app-id">${item.package_id}</div>
                            </td>
                            <td><div class="platform">${icon} ${item.platform}</div></td>
                            <td><span class="badge ${badgeClass}">${item.threat_type}</span></td>
                            <td style="color: ${item.risk_level === 'Critical' ? '#ef4444' : '#fbbf24'}; font-weight: 700;">${item.risk_level}</td>
                            <td>${statusHtml}</td>
                        </tr>
                        `;
                    });
                }
                
                tbody.innerHTML = html;
                document.getElementById('total-scams').innerText = data.total.toLocaleString();
                document.getElementById('page-info').innerText = `Page ${currentPage}`;
                
                document.getElementById('prev-btn').disabled = currentPage === 1;
                document.getElementById('next-btn').disabled = (currentPage * limit) >= data.total;
                
            } catch (err) {
                console.error("Failed to load data:", err);
            }
        }

        function changePage(delta) {
            currentPage += delta;
            if(currentPage < 1) currentPage = 1;
            loadData();
        }

        document.getElementById('search-input').addEventListener('input', (e) => {
            currentSearch = e.target.value;
            currentPage = 1;
            loadData();
        });

        loadData();
"""

# Replace the content of the <script> tag
code = re.sub(r'<script>.*?</script>', f'<script>\n{new_script}\n    </script>', code, flags=re.DOTALL)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)
