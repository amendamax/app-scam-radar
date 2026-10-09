import re

with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# Add background to body
code = re.sub(r'body\s*\{[^}]*\}', '''body {
            background-color: var(--bg-color);
            background-image: 
                linear-gradient(to bottom, rgba(3, 6, 10, 0.9), rgba(3, 6, 10, 0.97)),
                url('static/bg.jpg');
            background-size: cover;
            background-position: center top;
            background-attachment: fixed;
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
        }''', code)

# Add footer before </body>
footer_html = '''
    <style>
        .vasile-ecosystem-footer {
            background: rgba(3, 6, 10, 0.95);
            border-top: 1px solid rgba(255,255,255,0.05);
            padding: 40px 20px;
            margin-top: 60px;
            text-align: center;
        }
        .ecosystem-title {
            font-family: 'Outfit', sans-serif;
            color: #94a3b8;
            font-size: 14px;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 24px;
            font-weight: 700;
        }
        .ecosystem-grid {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 16px;
            max-width: 1000px;
            margin: 0 auto;
        }
        .eco-link {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
            padding: 10px 20px;
            border-radius: 8px;
            color: #cbd5e1;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.2s;
        }
        .eco-link:hover {
            background: rgba(239, 68, 68, 0.1);
            border-color: rgba(239, 68, 68, 0.3);
            color: white;
            transform: translateY(-2px);
        }
        .eco-link i { color: #ef4444; }
        .eco-copyright {
            margin-top: 40px;
            color: #475569;
            font-size: 13px;
        }
    </style>
    
    <footer class="vasile-ecosystem-footer">
        <div class="ecosystem-title">Official VasileDev Network</div>
        <div class="ecosystem-grid">
            <a href="https://vasiledev.com" class="eco-link"><i class="fa-solid fa-code"></i> VasileDev</a>
            <a href="https://isbrokersafe.com" class="eco-link"><i class="fa-solid fa-shield-halved"></i> IsBrokerSafe</a>
            <a href="https://verifydating.net" class="eco-link"><i class="fa-solid fa-heart-crack"></i> VerifyDating</a>
            <a href="https://jobscamradar.com" class="eco-link"><i class="fa-solid fa-briefcase"></i> JobScamRadar</a>
            <a href="https://pillscamradar.com" class="eco-link"><i class="fa-solid fa-pills"></i> PillScamRadar</a>
            <a href="#" class="eco-link" style="border-color: #ef4444; background: rgba(239, 68, 68, 0.1);"><i class="fa-solid fa-bug"></i> AppScamRadar</a>
            <a href="https://dreamcarhunt.com" class="eco-link"><i class="fa-solid fa-car"></i> DreamCarHunt</a>
            <a href="https://airparkrefund.com" class="eco-link"><i class="fa-solid fa-plane-departure"></i> AirParkRefund</a>
        </div>
        <div class="eco-copyright">
            &copy; 2024-2026 VasileDev Ecosystem. All rights reserved.<br>
            Protecting consumers against global digital fraud.
        </div>
    </footer>
'''

code = code.replace("</body>", f"{footer_html}\n</body>")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

