import winsound

def play_success_beep():
    """Phát tiếng bíp thông báo thành công trên Windows"""
    try:
        winsound.Beep(1000, 200)
    except:
        pass
