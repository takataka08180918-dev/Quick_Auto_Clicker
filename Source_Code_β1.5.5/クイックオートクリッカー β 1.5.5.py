import ctypes
import time
import keyboard   # 第三者ライブラリー
import os

# 定数定義
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

# 高速クリック関数（関数呼び出しのオーバーヘッド削減）
mouse_event = ctypes.windll.user32.mouse_event

# 左クリック
def click_left():
    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

# 右クリック
def click_right():
    mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

# 待機秒の補正
def difference_correction(cps_s):
    cps = 1 / cps_s
    if cps < 0.0005:  # 0.5ms未満はsleep誤差が大きいため補正
        cps = 0.0005
    return(cps)

# デイレクトリ取得
def get_base_path():
    import sys
    if getattr(sys, 'frozen', False):
        # PyInstaller でビルドされた exe の場所
        return os.path.dirname(sys.executable)
    else:
        # 通常の python 実行
        return os.path.dirname(os.path.abspath(__file__))

# txtから情報を取得
def get_value_by_key(file_path, target_key):
    base = get_base_path()
    full_path = os.path.join(base, file_path)

    with open(full_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                try:
                    if key == target_key:
                        return int(value)
                except ValueError:
                    return value
    return None

# txtファイルがないときの作成
def create_txt_if_not_exists(filename: str, lines: list):
    base = get_base_path()

    if not filename.endswith(".txt"):
        filename += ".txt"

    path = os.path.join(base, filename)

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(str(line))
        print("")
        print(f"{path} を新規作成しました。")
        print("")

# 押されたキー取得
def input_key(msg):
    time.sleep(0.2)
    print(msg, end="", flush=True)
    key_select = keyboard.read_key()
    print(key_select)
    return key_select

# メイン
def main():
    # txtから設定の読み込み
    setting_list = [
        "キーの変更は、以下の = の後にあるキーの名前を指定して変更できます(ファンクションキーは、f+~)\n"
        "key_exit = f7\n"
        "key_left = r\n"
        "key_right = t\n"
        "key_lock = v\n"
        "key_change_speed = :\n"
        "key_quick_up = .\n"
        "key_quick_down = ,\n"
    ]
    create_txt_if_not_exists("初期設定.txt", setting_list)

    # フラグ
    auto_click_left = False
    auto_click_right = False
    b_k = False
    cps_t = False
    a_redo = False
    c_f = 1
    
    # 初期キー割り当て
    key_exit = get_value_by_key("初期設定.txt", "key_exit")
    key_left = get_value_by_key("初期設定.txt", "key_left")
    key_right = get_value_by_key("初期設定.txt", "key_right")
    key_lock = get_value_by_key("初期設定.txt", "key_lock")
    key_change_speed = get_value_by_key("初期設定.txt", "key_change_speed")
    key_quick_up = get_value_by_key("初期設定.txt", "key_quick_up")
    key_quick_down = get_value_by_key("初期設定.txt", "key_quick_down")

    # 実行中の情報
    def information_now(cps_s, cps, state_left, state_right):
        os.system("cls")
        print("")
        print(key_exit+" >終了キー / "+key_left+" >左キー / "+key_right+" >右キー / "+key_lock+" >ロックキー / "+key_change_speed+" >速度変更キー")
        print(key_quick_up+" >クイック速度変更キー(アップ) / "+key_quick_down+" >クイック速度変更キー(ダウン)")
        print("")
        if cps_s == "t":
            print(f"待機秒:{cps}で実行中")
        else:
            print(f"cps:{cps_s}で実行中")
        print('\033[32m' + "ロック_左: " + ('\033[31m'+"ON" if state_left == True else "OFF"))
        print('\033[33m' + "ロック_右: " + ('\033[31m'+"ON" if state_right == True else "OFF") + '\033[0m')

    # メインループ
    while True:
        if b_k:
            break

        # CPS入力
        while True:
            try:
                # キー割り当てリトライ判定
                if a_redo == True:
                    cps_s = "c"
                else:
                    print("=================================================================================")
                    print("c: 割り当てキー変更、 / f: 1クリック周期のクリック数変更、 / t: 秒単位待機実行")
                    print("r: キー割り当てリセット  //  exit: 終了")
                    print("=================================================================================")
                    cps_s = input("CPS: ")
                
                #コマンド判定
                if cps_s == "c":
                    key_exit = input_key("終了キー:")
                    key_left = input_key("左キー:")
                    key_right = input_key("右キー:")
                    key_lock = input_key("ロックキー:")
                    key_change_speed = input_key("速度変更キー:")
                    key_quick_up = input_key("クイック速度変更キー（アップ）:")
                    key_quick_down = input_key("クイック速度変更キー（ダウン）:")

                    judgement_list = [key_exit, key_left, key_right, key_lock, key_change_speed, key_quick_up, key_quick_down]
                    if len(judgement_list) != len(set(judgement_list)):
                        if input_key("割り当てに重複があります。やり直しますか？ (y/n):") == "y":
                            a_redo = True
                        else:
                            os.system("cls")
                            a_redo = False
                    else:
                        os.system("cls")
                        a_redo = False

                elif cps_s == "f":
                    c_f = int(input("1クリック周期:"))
                    os.system("cls")

                elif cps_s == "t":
                    cps = int(input("待機秒数:"))
                    if cps > 0:
                        cps_t = True
                        break

                elif cps_s == "r":
                    key_exit = get_value_by_key("初期設定.txt", "key_exit")
                    key_left = get_value_by_key("初期設定.txt", "key_left")
                    key_right = get_value_by_key("初期設定.txt", "key_right")
                    key_lock = get_value_by_key("初期設定.txt", "key_lock")
                    key_change_speed = get_value_by_key("初期設定.txt", "key_change_speed")
                    key_quick_up = get_value_by_key("初期設定.txt", "key_quick_up")
                    key_quick_down = get_value_by_key("初期設定.txt", "key_quick_down")
                    print("初期設定.txtの内容でキー割り当てをリセットしました。")
                    time.sleep(1)
                    os.system("cls")

                elif cps_s == "exit":
                    print(">>exit")
                    b_k = True
                    break

                else:
                    cps_s = int(cps_s)
                    if cps_s > 0:
                        cps_t = False
                        break
                    else:
                        os.system("cls")
                        print('\033[31m'+">>>入力が正しくありません"+'\033[0m')
            except ValueError:
                os.system("cls")
                print('\033[31m'+">>>入力が正しくありません"+'\033[0m')
        
        if b_k:
            break

        # クリック間隔（理論上限界まで短く）
        if cps_t == False:
            cps = difference_correction(cps_s)

        # クリック実行ループ
        auto_click_left = False
        auto_click_right = False
        information_now(cps_s, cps, auto_click_left, auto_click_right)
        while True:
            start = time.perf_counter()

            # 終了
            if keyboard.is_pressed(key_exit):
                print(">>exit")
                b_k = True
                break
            
            # クイック速度変更
            if cps_t == False:
                if keyboard.is_pressed(key_quick_up):
                    cps_s += 2
                    cps = difference_correction(cps_s)
                    information_now(cps_s, cps, auto_click_left, auto_click_right)
                elif keyboard.is_pressed(key_quick_down):
                    if not cps_s - 2 <= 0:
                        cps_s -= 2
                    cps = difference_correction(cps_s)
                    information_now(cps_s, cps, auto_click_left, auto_click_right)

            # 左クリックトグル
            if keyboard.is_pressed(key_lock) and keyboard.is_pressed(key_left):
                auto_click_left = not auto_click_left
                information_now(cps_s, cps, auto_click_left, auto_click_right)
                while keyboard.is_pressed(key_lock) or keyboard.is_pressed(key_left):
                    time.sleep(0.05)

            # 右クリックトグル
            if keyboard.is_pressed(key_lock) and keyboard.is_pressed(key_right):
                auto_click_right = not auto_click_right
                information_now(cps_s, cps, auto_click_left, auto_click_right)
                while keyboard.is_pressed(key_lock) or keyboard.is_pressed(key_right):
                    time.sleep(0.05)

            # 高速クリック処理
            if auto_click_left or keyboard.is_pressed(key_left):
                if c_f > 1:
                    for _ in range(c_f):
                        click_left()
                        time.sleep(0.05)
                else:
                    click_left()
            if auto_click_right or keyboard.is_pressed(key_right):
                if c_f > 1:
                    for _ in range(c_f):
                        click_right()
                        time.sleep(0.05)
                else:
                    click_right()

            # 高精度ウェイト
            elapsed = time.perf_counter() - start
            remaining = cps - elapsed
            if remaining > 0:
                time.sleep(remaining)

            # 速度変更判定
            if keyboard.is_pressed(key_change_speed):
                break
        
        if b_k == False:
            os.system("cls")

if __name__ == "__main__":
    main()
