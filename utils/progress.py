import time
import math

def get_progress_bar(percent):
    done = int(percent / 10)
    return "●" * done + "○" * (10 - done)

def format_eta(seconds):
    if seconds is None or seconds < 0:
        return "Calculating..."
    if seconds > 3600:
        return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes}m {seconds}s"

def get_network_status(speed_mb):
    if speed_mb > 5: return "🚀 Fast"
    if speed_mb > 1: return "📶 Stable"
    return "🐌 Slow"

class ProgressTracker:
    def __init__(self):
        self.last_update_time = 0
        self.start_time = time.time()

    async def update_progress(self, message, current, total, filename, texts, is_done=False):
        now = time.time()
        
        # Final update when done
        if is_done:
            text = f"✅ <b>{texts['done']}!</b>\n📄 <code>{filename[:35]}</code>"
            try:
                await message.edit_text(text, parse_mode='HTML')
            except:
                pass
            return

        # 3 second delay to avoid Telegram flood limits
        if now - self.last_update_time < 3:
            return
        
        self.last_update_time = now
        
        if total <= 0: return
        
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
            f"📄 <code>{filename[:35]}</code>\n"
            f"<b>{texts['downloading']}</b>\n\n"
            f"<code>[{bar}]</code>\n"
            f"◌ <b>{texts['progress']}</b> : 〘 {pct}% 〙\n"
            f"✅ <b>{texts['done']}</b>        : 〘 {dmb:.2f} MB of {tmb:.2f} MB 〙\n"
            f"🚀 <b>{texts['speed']}</b>       : 〘 {smb:.2f} MB/s 〙\n"
            f"⏳ <b>{texts['eta']}</b>         : 〘 {eta_fmt} 〙\n"
            f"📶 <b>{texts['network']}</b>     : {net}"
        )
        
        try:
            await message.edit_text(text, parse_mode='HTML')
        except Exception:
            pass
