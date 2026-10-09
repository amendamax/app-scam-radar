import sqlite3
import datetime

DB_PATH = "app_scams.db"

def seed_demo_malware():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 20 real recent Android/iOS malware campaigns
    malware_data = [
        ("Vultur Trojan", "com.secure.authenticator.pro", "Google Play", "Banking Trojan", "Critical", "Removed", "Steals bank login credentials via keylogging and screen recording."),
        ("Xenomorph", "com.fast.cleaner.battery", "Google Play", "Banking Trojan", "Critical", "Removed", "Targets 50+ European banks. Overlays fake login screens."),
        ("SharkBot", "com.antivirus.super.cleaner", "Google Play", "Banking Trojan", "Critical", "Active", "Initiates money transfers from compromised devices automatically."),
        ("FluBot", "com.dhl.tracking.delivery", "Third-party APK", "SMS Worm", "Critical", "Active", "Spreads via SMS. Steals passwords and contact lists."),
        ("Joker Spyware", "com.color.message.sms", "Google Play", "Spyware / Billing Fraud", "High", "Removed", "Subscribes victims to premium SMS services without consent."),
        ("Facestealer", "com.photo.editor.pro.fx", "Google Play", "Credential Harvester", "Critical", "Removed", "Steals Facebook credentials using a fake login prompt."),
        ("Autolycos", "com.camera.filters.sweet", "Google Play", "Fleeceware", "High", "Removed", "Subscribes users to premium services behind the scenes."),
        ("Goldoson", "com.step.counter.pedometer", "Google Play", "Adware / Spyware", "Medium", "Removed", "Clicks background ads and steals device data (GPS, MAC)."),
        ("Teabot", "com.qr.code.reader.scanner", "Google Play", "Banking Trojan", "Critical", "Removed", "Intercepts SMS codes and logs keystrokes."),
        ("Pegasus", "N/A (Zero-click exploit)", "iOS / Android", "State-Sponsored Spyware", "Critical", "Active", "Advanced spyware targeting journalists and activists."),
        ("WhatsApp Pink", "com.whatsapp.pink.update", "Third-party APK", "Worm / Trojan", "Critical", "Active", "Promises a pink theme but steals data and spreads via contacts."),
        ("GravityRAT", "com.secure.chat.messenger", "Windows / Android", "Spyware", "High", "Active", "Exfiltrates files, contacts, and audio recordings."),
        ("Octo", "com.fake.chrome.browser", "Third-party APK", "Banking Trojan", "Critical", "Active", "Allows remote access and control of the device screen."),
        ("Anubis", "com.system.update.service", "Third-party APK", "Banking Trojan", "Critical", "Active", "Steals banking credentials and acts as ransomware."),
        ("AlienBot", "com.covid.tracker.app", "Third-party APK", "Banking Trojan", "Critical", "Removed", "Injects malicious code into legitimate financial apps."),
        ("Hydra", "com.video.downloader.free", "Google Play", "Banking Trojan", "Critical", "Removed", "Requests dangerous permissions to control the device."),
        ("Cerberus", "com.currency.converter.pro", "Google Play", "Banking Trojan", "Critical", "Removed", "Bypasses 2FA by intercepting SMS messages."),
        ("EventBot", "com.ms.word.reader", "Third-party APK", "Info Stealer", "High", "Active", "Steals financial data and crypto wallet seed phrases."),
        ("BRATA", "com.security.scanner.antivirus", "Google Play", "Banking Trojan", "Critical", "Removed", "Performs unauthorized wire transfers and factory resets the phone."),
        ("SpyHide", "com.hidden.tracker.gps", "Third-party APK", "Stalkerware", "High", "Active", "Monitors GPS, calls, and messages secretly.")
    ]
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    inserted = 0
    for app in malware_data:
        slug = app[0].lower().replace(" ", "-").replace("/", "-")
        try:
            c.execute('''
                INSERT INTO malicious_apps 
                (slug, app_name, package_id, platform, threat_type, risk_level, status, description, added_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (slug, app[0], app[1], app[2], app[3], app[4], app[5], app[6], today))
            inserted += 1
        except sqlite3.IntegrityError:
            pass
            
    conn.commit()
    conn.close()
    print(f"Seeded {inserted} top malware threats.")

if __name__ == "__main__":
    seed_demo_malware()
