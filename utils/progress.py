import time
import math

def get_progress_bar(percent):
    done = int(percent / 10)
    return "●" * done + "○" * (10 - done)

def format_eta(seconds):
    if seconds is None:
        return "Unknown"
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    return f"{minutes}m {seconds}s"

def get_network_status(speed_mb):
    if speed_mb > 10: return "🚀 Fast"
    if speed_mb > 2: return "📶 Stable"
    return "🐌 Slow"

class ProgressTracker:
    def __init__(self):
        self.last_update_time = 0
        self.start_time = time.time()

    async def update_progress(self, message, current, total, filename):
        now = time.time()
        # 3 second delay to avoid Telegram flood limits
        if now - self.last_update_time < 3:
            return
        
        self.last_update_time = now
        
        pct = round((current / total) * 100, 2)
        dmb = current / (1024 * 1024)
        tmb = total / (1024 * 1024)
        
        elapsed = now - self.start_time
        smb = dmb / elapsed if elapsed > 0 else 0
        eta = (total - current) / (smb * 1024 * 1024) if smb > 0 else 0
        
        bar = get_progress_bar(pct)
        eta_fmt = format_eta(eta)
        net = get_network_status(smb)
        
        text = (
            f"📄 ` {filename[:35]} `\n"
            f"*⬇️ Downloading from server...*\n\n"
            f"`[{bar}]`\n"
            f"◌ *Progress* 😉 : 〘 {pct}% 〙\n"
            f"✅ *Done*        : 〘 {dmb:.2f} MB of {tmb:.2f} MB 〙\n"
            f"🚀 *Speed*       : 〘 {smb:.2f} MB/s 〙\n"
            f"⏳ *ETA*         : 〘 {eta_fmt} 〙\n"
            f"📶 *Network*     : {net}"
        )
        
        try:
            await message.edit_text(text, parse_mode='Markdown')
        except Exception:
            pass
