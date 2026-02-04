import datetime
import os, sys, time
import ssl
from attr import s
import serial
from serial.tools import list_ports
import random
ssl._create_default_https_context = ssl._create_unverified_context
import cv2
from kivy.graphics.texture import Texture
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    running_mode = 'Frozen/executable'
else:
    try:
        app_full_path = os.path.realpath(__file__)
        application_path = os.path.dirname(app_full_path)
        running_mode = "Non-interactive"
    except NameError:
        application_path = os.getcwd()
        running_mode = 'Interactive'
logger_name = f'app.log'
logger_dir = os.path.join(application_path, "logs")

from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'system')

from kivy.logger import Logger
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager
from kivymd.font_definitions import theme_font_styles
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from kivymd.toast import toast
from kivymd.app import MDApp
import numpy as np
import configparser, hashlib, mysql.connector
from pymodbus.client import ModbusTcpClient
from fpdf import FPDF
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.graphics.texture import Texture

colors = {
    "Red"   : {"A200": "#FF2A2A","A500": "#FF8080","A700": "#FFD5D5",},
    "Gray"  : {"200": "#CCCCCC","500": "#ECECEC","700": "#F9F9F9",},
    "Blue"  : {"200": "#4471C4","500": "#5885D8","700": "#6C99EC",},
    "Green" : {"200": "#2CA02C","500": "#2DB97F", "700": "#D5FFD5",},
    "Yellow": {"200": "#ffD42A","500": "#ffE680","700": "#fff6D5",},
    "Light" : {"StatusBar": "E0E0E0","AppBar": "#202020","Background": "#EEEEEE","CardsDialogs": "#FFFFFF","FlatButtonDown": "#CCCCCC",},
    "Dark"  : {"StatusBar": "101010","AppBar": "#E0E0E0","Background": "#111111","CardsDialogs": "#222222","FlatButtonDown": "#DDDDDD",},
}

config_name = 'config.ini'
config_full_path = os.path.join(application_path, config_name)
config = configparser.ConfigParser()
config.read(config_full_path)

## App Setting
APP_TITLE = config['app']['APP_TITLE']
APP_SUBTITLE = config['app']['APP_SUBTITLE']
IMG_LOGO_PEMKAB = config['app']['IMG_LOGO_PEMKAB']
IMG_LOGO_DISHUB = config['app']['IMG_LOGO_DISHUB']
LB_PEMKAB = config['app']['LB_PEMKAB']
LB_DISHUB = config['app']['LB_DISHUB']
LB_UNIT = config['app']['LB_UNIT']
LB_UNIT_ADDRESS = config['app']['LB_UNIT_ADDRESS']

# SQL setting
DB_HOST = "194.31.53.37"
DB_USER = "Pndujikir2022!"  
DB_PASSWORD = "@Kirpnd2022!"

DB_NAME = "pkbpandeglang"
TB_DATA = "tb_cekident"
TB_USER = "users"
TB_MERK = "merk"
TB_BAHAN_BAKAR = "bahanbakar"
TB_WARNA = "warna"
TB_DATA_MASTER = "identkendaraan"

FTP_HOST = "194.31.53.37"
FTP_USER = "root"
FTP_PASS = "@D15HUBp2022!"

class ScreenHome(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenHome, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE        
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS

    def on_enter(self):
        Clock.schedule_interval(self.regular_update_carousel, 3)

    def on_leave(self):
        Clock.unschedule(self.regular_update_carousel)

    def regular_update_carousel(self, dt):
        try:
            self.ids.carousel.index += 1

        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Tampilan Carousel'
            toast_msg = f'Error Update Carousel: {e}'
            toast(toast_msg)                

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Error Navigate to Home Screen: {e}'
            toast(toast_msg)        

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast(f"Anda sudah login sebagai {dt_user}")

        except Exception as e:
            toast_msg = f'Terjadi kesalahan saat berpindah ke halaman Login'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Terjadi kesalahan saat berpindah ke halaman Utama'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

class ScreenLogin(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenLogin, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE  
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS

    def exec_cancel(self):
        try:
            self.ids.tx_username.text = ""
            self.ids.tx_password.text = ""    
        except Exception as e:
            toast_msg = f'error Login: {e}'

    def exec_login(self):
        global mydb, db_users
        global dt_id_user, dt_user, dt_foto_user
        screen_main = self.screen_manager.get_screen('screen_main')

        try:
            screen_main.exec_reload_database()
            input_username = self.ids.tx_username.text
            input_password = self.ids.tx_password.text        
            dataBase_password = input_password
            hashed_password = hashlib.md5(dataBase_password.encode())
            mycursor = mydb.cursor()
            mycursor.execute(f"SELECT id_user, nama, username, password, image FROM {TB_USER} WHERE username = '{input_username}' and password = '{hashed_password.hexdigest()}'")
            myresult = mycursor.fetchone()
            db_users = np.array(myresult).T
            
            if myresult is None:
                toast_msg = f'Gagal Masuk, Nama Pengguna atau Password Salah'
                toast(toast_msg) 
                Logger.warning(f"{self.name}: {toast_msg}") 
            else:
                toast_msg = f'Berhasil Masuk, Selamat Datang {myresult[1]}'
                toast(toast_msg)
                Logger.info(f"{self.name}: {toast_msg}")  
                dt_id_user = myresult[0]
                dt_user = myresult[1]
                dt_foto_user = myresult[4]
                self.ids.tx_username.text = ""
                self.ids.tx_password.text = "" 
                self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Gagal masuk, silahkan isi nama user dan password yang sesuai'
            toast(toast_msg)  
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Awal'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast_msg = f"Anda sudah login sebagai {dt_user}"
                toast(toast_msg)
                Logger.info(f"{self.name}: {toast_msg}")  

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Login'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Utama'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

class ScreenMain(MDScreen):   
    def __init__(self, **kwargs):
        super(ScreenMain, self).__init__(**kwargs)
        global dt_user, dt_foto_user, dt_no_antri, dt_no_pol, dt_no_uji, dt_sts_uji, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_brt_ksg, dt_bhn_bkr, dt_warna, dt_chasis, dt_no_mesin
        global dt_id_user
        global hlm_right_value, hlm_right_flag
        global hlm_left_value, hlm_left_flag
        global hlm_diff_right_value, hlm_diff_right_flag
        global hlm_diff_left_value, hlm_diff_left_flag
        global dt_dash_pendaftaran, dt_dash_belum_uji, dt_dash_sudah_uji
        global hlm_flag

        dt_user = dt_foto_user = dt_no_antri = dt_no_pol = dt_no_uji = dt_sts_uji = dt_nama = ""
        dt_merk = dt_type = dt_jns_kend = dt_jbb = dt_brt_ksg = dt_bhn_bkr = dt_warna = dt_chasis = dt_no_mesin = ""
        dt_id_user = 1
        dt_dash_pendaftaran = dt_dash_belum_uji = dt_dash_sudah_uji = 0
        
        hlm_right_value = hlm_right_flag = 2
        hlm_left_value = hlm_left_flag = 2
        hlm_diff_right_value = hlm_diff_right_flag = 2
        hlm_diff_left_value = hlm_diff_left_flag = 2
        hlm_flag = 2 

        Clock.schedule_once(self.delayed_init, 1)

    def delayed_init(self, dt):   
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE              
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS
        
        Clock.schedule_interval(self.regular_update_display, 1)

    def on_enter(self):
        self.exec_reload_database()
        self.exec_reload_table()

    def regular_update_display(self, dt):
        try:
            current_time = str(time.strftime("%H:%M:%S", time.localtime()))
            current_date = str(time.strftime("%d/%m/%Y", time.localtime()))
            
            screens_to_update = ['screen_home', 'screen_login', 'screen_Head_lamp', 'screen_Calibration']
            for screen_name in screens_to_update:
                screen = self.screen_manager.get_screen(screen_name)
                screen.ids.lb_time.text = current_time
                screen.ids.lb_date.text = current_date

            self.ids.lb_time.text = current_time
            self.ids.lb_date.text = current_date
            self.ids.lb_dash_pendaftaran.text = str(dt_dash_pendaftaran)
            self.ids.lb_dash_belum_uji.text = str(dt_dash_belum_uji)
            self.ids.lb_dash_sudah_uji.text = str(dt_dash_sudah_uji)
            
            login_text = f'Login Sebagai: \n{dt_user}' if dt_user else 'Silahkan Login'
            user_image = f'https://{FTP_HOST}/ujikir/foto_user/{dt_foto_user}' if dt_user else 'assets/images/icon-login.png'

            for screen_name in ['screen_home', 'screen_login', 'screen_Head_lamp', 'screen_Calibration']:
                try:
                    screen = self.screen_manager.get_screen(screen_name)
                    screen.ids.lb_operator.text = login_text
                    if hasattr(screen.ids, 'img_user'):
                        screen.ids.img_user.source = user_image
                except (KeyError, AttributeError):
                    pass
            
            self.ids.lb_operator.text = login_text
            self.ids.img_user.source = user_image
            self.ids.bt_logout.disabled = not dt_user

        except Exception as e:
            toast('Gagal Memperbaharui Tampilan')
            Logger.error(f"{self.name}: Update Display Error, {e}")

    def exec_reload_database(self):
        global mydb
        try:
            mydb = mysql.connector.connect(host = DB_HOST,user = DB_USER,password = DB_PASSWORD, database = DB_NAME)
        except Exception as e:
            toast_msg = f'Gagal Menginisiasi Database'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_reload_table(self):
        print("\n--- FUNGSI exec_reload_table (VERSI PERBAIKAN) DIPANGGIL ---")
        global mydb, db_antrian, db_merk, db_bahan_bakar, db_warna
        global dt_dash_pendaftaran, dt_dash_belum_uji, dt_dash_sudah_uji

        try:
            cursor = mydb.cursor()
            today = str(time.strftime("%Y-%m-%d", time.localtime()))

            cursor.execute(f"SELECT ID, DESCRIPTION FROM {TB_MERK}")
            db_merk = np.array(cursor.fetchall())
            cursor.execute(f"SELECT id_warna, nama FROM {TB_WARNA}")
            db_warna = np.array(cursor.fetchall())
            
            query_pendaftaran = f"SELECT COUNT(*) FROM {TB_DATA} WHERE DATE(tgl_daftar) = %s"
            cursor.execute(query_pendaftaran, (today,))
            dt_dash_pendaftaran = cursor.fetchone()[0] or 0

            query_sudah_uji = f"SELECT COUNT(*) FROM {TB_DATA} WHERE DATE(tgl_daftar) = %s AND hlm_flag IN (0, 1)"
            cursor.execute(query_sudah_uji, (today,))
            dt_dash_sudah_uji = cursor.fetchone()[0] or 0
            
            dt_dash_belum_uji = dt_dash_pendaftaran - dt_dash_sudah_uji
            
            query_table = f"""
                SELECT noantrian, nopol, nouji, statusuji, merk, type, idjeniskendaraan, 
                    warna, th_buat, hlm_flag 
                FROM {TB_DATA} 
                WHERE hlm_flag = 2 AND DATE(tgl_daftar) = %s
            """
            cursor.execute(query_table, (today,))
            result_tb_antrian = cursor.fetchall()
            
            db_antrian = np.array(result_tb_antrian).T if result_tb_antrian else np.array([])
            cursor.close()

        except Exception as e:
            toast('Gagal mengambil data antrian harian')
            Logger.error(f"{self.name}: Reload Table Error, {e}")
            return
        
        try:
            layout_list = self.ids.layout_list
            layout_list.clear_widgets()
            if db_antrian.size == 0:
                layout_list.add_widget(MDLabel(text="Semua kendaraan sudah diuji lampu.", halign="center", theme_text_color="Secondary"))
                return

            for i in range(db_antrian.shape[1]):
                merk_id = db_antrian[4, i]
                merk_name_row = db_merk[db_merk[:, 0] == merk_id]
                merk_text = merk_name_row[0, 1] if merk_name_row.size > 0 else '-'

                warna_id = db_antrian[7, i] # Indeks ke-7 sekarang adalah 'warna'
                warna_name_row = db_warna[db_warna[:, 0] == warna_id]
                warna_text = warna_name_row[0, 1] if warna_name_row.size > 0 else '-'
                
                hlm_flag_val = int(db_antrian[9, i]) if db_antrian[9, i] is not None else 2
                lampu_stat = 'Lulus' if hlm_flag_val == 1 else 'Tidak Lulus' if hlm_flag_val == 0 else 'Belum Uji'
                
                layout_list.add_widget(
                    MDCard(
                        MDLabel(text=f"{db_antrian[0, i]}", halign="center", size_hint_x=0.06),
                        MDLabel(text=f"{db_antrian[1, i]}", halign="center", size_hint_x=0.08), 
                        MDLabel(text=f"{db_antrian[2, i]}", halign="center", size_hint_x=0.09), 
                        MDLabel(text='Berkala' if db_antrian[3, i] == 'B' else 'Uji Ulang', halign="center", size_hint_x=0.07), 
                        MDLabel(text=merk_text, halign="center", size_hint_x=0.10),             
                        MDLabel(text=f"{db_antrian[5, i]}", halign="center", size_hint_x=0.12), 
                        MDLabel(text=f"{db_antrian[6, i]}", halign="center", size_hint_x=0.15), 
                        MDLabel(text=warna_text, halign="center", size_hint_x=0.08),            
                        MDLabel(text=f"{db_antrian[8, i]}", halign="center", size_hint_x=0.07), 
                        MDLabel(text=lampu_stat, halign="center", size_hint_x=0.08),           
                        ripple_behavior=True,
                        on_press=self.on_antrian_row_press,
                        padding="10dp", id=f"card_antrian{i}",
                        size_hint_y=None, height=dp(40)
                    )
                )
        except Exception as e:
            toast('Gagal memuat ulang tabel antrian')
            Logger.error(f"{self.name}: Gagal render tabel, {e}")
        
        self.exec_reload_database()

    def on_antrian_row_press(self, instance):
        global dt_user, dt_no_antri, dt_no_pol, dt_no_uji, dt_sts_uji, dt_merk, dt_type
        global dt_jns_kend, dt_jbb, dt_brt_ksg, dt_bhn_bkr, dt_warna, dt_nama, dt_thn_buat, hlm_flag

        try:
            if not dt_user:
                toast("Silakan login terlebih dahulu.")
                return

            row = int(str(instance.id).replace("card_antrian", ""))
            dt_no_antri = db_antrian[0, row]
            dt_no_pol = db_antrian[1, row]
            dt_no_uji = db_antrian[2, row]
            dt_sts_uji = db_antrian[3, row]
            dt_merk = db_antrian[4, row]
            dt_type = db_antrian[5, row]
            dt_jns_kend = db_antrian[6, row]
            dt_warna = db_antrian[7, row]
            dt_thn_buat = db_antrian[8, row]
            hlm_flag = int(db_antrian[9, row])
            
            self.screen_manager.current = 'screen_Head_lamp'

        except Exception as e:
            toast('Gagal memproses data antrian')
            Logger.error(f"{self.name}: Row Press Error, {e}")

    def exec_logout(self):
        global dt_user
        dt_user = ""
        self.screen_manager.current = 'screen_login'

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'
        except Exception as e:
            toast_msg = f'Terjadi kesalahan saat berpindah ke halaman Beranda'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")   

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast_msg = f"Anda sudah login sebagai {dt_user}"
                toast(toast_msg)
                Logger.info(f"{self.name}: {toast_msg}")
        except Exception as e:
            toast_msg = f'Terjadi kesalahan saat berpindah ke halaman Login'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")      

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Terjadi kesalahan saat berpindah ke halaman Utama'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")    

class ScreenHeadlamp(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenHeadlamp, self).__init__(**kwargs)
        self.capture = None
        self.camera_event = None
        self.camera_is_on = False
        self.test_beam = 'jauh'
        self.test_side = 'kiri'

        # PERBAIKAN: Struktur data baru untuk menyimpan hasil lebih detail
        self.test_results = {}
        self._reset_test_results()

        self.current_cd = 0
        self.current_dev_h = 0
        self.current_dev_v = 0
        self.countdown_seconds = config.getint('headlamp_settings', 'count_starting_lamp', fallback=5)
        self.countdown_event = None

        try:
            config.read(config_full_path)
            self.CAMERA_ID = config.getint('headlamp_settings', 'camera_id', fallback=1)
            self.TEST_DISTANCE_METERS = config.getfloat('headlamp_settings', 'test_distance_meters')
            self.CAM_WIDTH = config.getint('headlamp_settings', 'camera_width')
            self.CAM_HEIGHT = config.getint('headlamp_settings', 'camera_height')
            self.REF_POINT_X = config.getint('headlamp_settings', 'ref_point_x')
            self.REF_POINT_Y = config.getint('headlamp_settings', 'ref_point_y')
            self.PIXELS_PER_DEGREE_HORIZONTAL = config.getfloat('headlamp_settings', 'pixels_per_degree_horizontal')
            self.MM_PER_PIXEL_VERTICAL = config.getfloat('headlamp_settings', 'mm_per_pixel_vertical')
            self.MIN_CANDELA_THRESHOLD = config.getfloat('headlamp_settings', 'min_candela_lulus')
            self.MAX_DEVIATION_RIGHT_DEG = config.getfloat('headlamp_settings', 'max_deviation_right_deg')
            self.MAX_DEVIATION_LEFT_DEG = config.getfloat('headlamp_settings', 'max_deviation_left_deg')
            self.MAX_VERTICAL_DEVIATION_PERCENT = config.getfloat('headlamp_settings', 'max_vertical_deviation_percent')
            self.LUX_TO_CANDELA_FACTOR = self.TEST_DISTANCE_METERS ** 2
            Logger.info(f"{self.name}: Pengaturan Headlamp berhasil dimuat.")
        except Exception as e:
            toast("Gagal memuat config.ini, menggunakan nilai default.")
            Logger.error(f"{self.name}: Error saat membaca config.ini: {e}")
            # Fallback values
            self.TEST_DISTANCE_METERS, self.CAM_WIDTH, self.CAM_HEIGHT = 1.0, 640, 480
            self.REF_POINT_X, self.REF_POINT_Y = 320, 240
            self.PIXELS_PER_DEGREE_HORIZONTAL, self.MM_PER_PIXEL_VERTICAL = 50.0, 1.5
            self.MIN_CANDELA_THRESHOLD = 12000.0
            self.MAX_DEVIATION_RIGHT_DEG, self.MAX_DEVIATION_LEFT_DEG = 0.57, 1.15
            self.MAX_VERTICAL_DEVIATION_PERCENT = 1.3
            self.LUX_TO_CANDELA_FACTOR = self.TEST_DISTANCE_METERS ** 2

        Clock.schedule_once(self.delayed_init, 1)

    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS

    # PERBAIKAN: Struktur data baru
    def _reset_test_results(self):
        """Mereset struktur data untuk menyimpan hasil yang lebih detail."""
        default_result = {'cd': 0, 'dev_h': 0, 'dev_v': 0,
                          'intensity_flag': 2, 'deviation_flag': 2, 'status': 2}
        self.test_results = {
            'jauh_kiri': default_result.copy(),
            'jauh_kanan': default_result.copy(),
            'dekat_kiri': default_result.copy(),
            'dekat_kanan': default_result.copy()
        }


    def on_leave(self, *args):
        if self.camera_is_on: self.stop_camera()
        if self.countdown_event: self.countdown_event.cancel(); self.countdown_event = None


    def on_enter(self, *args):
        """Dipanggil saat layar ditampilkan."""
        try:
            config.read(config_full_path)
            self.INTENSITY_SLOPE = config.getfloat('camera_calibration', 'intensity_slope')
            self.INTENSITY_INTERCEPT = config.getfloat('camera_calibration', 'intensity_intercept')
            self.CAMERA_EXPOSURE = config.getfloat('camera_calibration', 'exposure', fallback=-4)
        except Exception:
            self.INTENSITY_SLOPE, self.INTENSITY_INTERCEPT, self.CAMERA_EXPOSURE = 1.0, 0.0, -4
        try:
            self.ids.lb_no_antrian.text = str(dt_no_antri)
            self.ids.lb_no_pol.text = str(dt_no_pol)
            self.ids.lb_no_uji.text = str(dt_no_uji)
        except Exception as e:
            Logger.error(f"{self.name}: Gagal mengisi label identitas - {e}")
        
        self._reset_test_results()
        self.ids.camera_view.texture = None
        self.ids.lb_countdown.text = ""
        self.ids.lb_test_result.text = "-"
        
        # Atur status DAN warna default saat layar dibuka
        self.select_beam('jauh')
        self.select_side('kiri')

    def select_beam(self, beam_type):
        """Mengatur jenis lampu dan mengubah warna background, teks, dan ikon."""
        self.test_beam = beam_type
        
        selected_color = self.theme_cls.colors["Blue"]["200"] 
        unselected_color = (0.9, 0.9, 0.9, 1)
        
        # Atur warna background
        self.ids.btn_jauh.md_bg_color = selected_color if beam_type == 'jauh' else unselected_color
        self.ids.btn_dekat.md_bg_color = selected_color if beam_type == 'dekat' else unselected_color
        
        # PERBAIKAN: Atur warna teks DAN ikon agar kontras
        self.ids.btn_jauh.text_color = "white" if beam_type == 'jauh' else "black"
        self.ids.btn_jauh.icon_color = "white" if beam_type == 'jauh' else "black"
        
        self.ids.btn_dekat.text_color = "white" if beam_type == 'dekat' else "black"
        self.ids.btn_dekat.icon_color = "white" if beam_type == 'dekat' else "black"
            
        self._update_info_panel()

    def select_side(self, side_type):
        """Mengatur sisi lampu dan mengubah warna background, teks, dan ikon."""
        self.test_side = side_type
        
        selected_color = self.theme_cls.colors["Blue"]["200"]
        unselected_color = (0.9, 0.9, 0.9, 1)
        
        # Atur warna background
        self.ids.btn_kiri.md_bg_color = selected_color if side_type == 'kiri' else unselected_color
        self.ids.btn_kanan.md_bg_color = selected_color if side_type == 'kanan' else unselected_color
        
        # PERBAIKAN: Atur warna teks DAN ikon agar kontras
        self.ids.btn_kiri.text_color = "white" if side_type == 'kiri' else "black"
        self.ids.btn_kiri.icon_color = "white" if side_type == 'kiri' else "black"

        self.ids.btn_kanan.text_color = "white" if side_type == 'kanan' else "black"
        self.ids.btn_kanan.icon_color = "white" if side_type == 'kanan' else "black"
            
        self._update_info_panel()

    def _update_info_panel(self):
            """Memperbarui semua label informasi di panel kanan, termasuk status kelulusan."""
            key = f"{self.test_beam}_{self.test_side}"
            result = self.test_results.get(key, {})
            
            # Update info bagian dan nilai terukur (tetap sama)
            bagian_uji = f"Lampu {self.test_beam.capitalize()} {self.test_side.capitalize()}"
            self.ids.lb_info_bagian.text = bagian_uji
            self.ids.lb_info_daya.text = f"{result.get('cd', 0):.0f} Cdl"
            dev_h, dev_v = result.get('dev_h', 0), result.get('dev_v', 0)
            dev_h_text = f"{abs(dev_h):.2f}° {'Kiri' if dev_h < 0 else 'Kanan'}"
            dev_v_text = f"{abs(dev_v):.2f}% {'Bawah' if dev_v < 0 else 'Atas'}"
            self.ids.lb_info_penyimpangan.text = f"H: {dev_h_text} | V: {dev_v_text}"

            # PERBAIKAN: Logika baru untuk mengisi label status
            # Status Daya Pancar
            intensity_flag = result.get('intensity_flag', 2) # 2 = Belum diuji
            if intensity_flag == 1:
                self.ids.lb_info_daya_status.text = "(LULUS)"
                self.ids.lb_info_daya_status.text_color = (0.2, 0.8, 0.2, 1) # Hijau
            elif intensity_flag == 0:
                self.ids.lb_info_daya_status.text = "(TIDAK LULUS)"
                self.ids.lb_info_daya_status.text_color = (1, 0.2, 0.2, 1) # Merah
            else:
                self.ids.lb_info_daya_status.text = "(-)"
                self.ids.lb_info_daya_status.text_color = "white"

            # Status Penyimpangan
            deviation_flag = result.get('deviation_flag', 2) # 2 = Belum diuji
            if deviation_flag == 1:
                self.ids.lb_info_penyimpangan_status.text = "(LULUS)"
                self.ids.lb_info_penyimpangan_status.text_color = (0.2, 0.8, 0.2, 1) # Hijau
            elif deviation_flag == 0:
                self.ids.lb_info_penyimpangan_status.text = "(TIDAK LULUS)"
                self.ids.lb_info_penyimpangan_status.text_color = (1, 0.2, 0.2, 1) # Merah
            else:
                self.ids.lb_info_penyimpangan_status.text = "(-)"
                self.ids.lb_info_penyimpangan_status.text_color = "white"

    def exec_open_camera(self):
        if self.camera_is_on: self.stop_camera()
        else: self.start_camera()

    def exec_start_test(self):
        if not self.camera_is_on: toast("Kamera belum dibuka. Tekan 'BUKA' terlebih dahulu."); return
        if self.countdown_event: toast("Pengujian sedang berjalan."); return
        self.countdown_value = self.countdown_seconds
        self.ids.lb_countdown.text = str(self.countdown_value)
        self.countdown_event = Clock.schedule_interval(self._update_countdown, 1)

    def _update_countdown(self, dt):
        self.countdown_value -= 1
        self.ids.lb_countdown.text = str(self.countdown_value) if self.countdown_value > 0 else "Selesai!"
        if self.countdown_value <= 0: self._finish_test()

    def _finish_test(self):
        if self.countdown_event: self.countdown_event.cancel(); self.countdown_event = None
        key = f"{self.test_beam}_{self.test_side}"
        
        # PERBAIKAN: Panggil fungsi baru untuk mendapatkan semua status
        intensity_flag, deviation_flag, overall_status = self._calculate_pass_fail(
            self.current_cd, self.current_dev_h, self.current_dev_v, self.test_side)

        # Simpan semua data ke dictionary
        self.test_results[key]['cd'] = self.current_cd
        self.test_results[key]['dev_h'] = self.current_dev_h
        self.test_results[key]['dev_v'] = self.current_dev_v
        self.test_results[key]['intensity_flag'] = intensity_flag
        self.test_results[key]['deviation_flag'] = deviation_flag
        self.test_results[key]['status'] = overall_status

        # Update UI
        self.ids.lb_test_result.text = "LULUS" if overall_status else "TIDAK LULUS"
        self.ids.lb_test_result.md_bg_color = (0,0.7,0,1) if overall_status else (0.9,0,0,1)
        self._update_info_panel()
        Clock.schedule_once(lambda dt: setattr(self.ids.lb_countdown, 'text', ''), 1)

    def start_camera(self):
        # self.capture = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.capture = cv2.VideoCapture(self.CAMERA_ID, cv2.CAP_DSHOW)
        if not self.capture.isOpened(): toast("Error: Tidak dapat membuka kamera."); self.capture = None; return
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.CAM_WIDTH)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.CAM_HEIGHT)
        self.capture.set(cv2.CAP_PROP_EXPOSURE, self.CAMERA_EXPOSURE)
        self.camera_event = Clock.schedule_interval(self.update_camera_feed, 1.0 / 30.0)
        self.camera_is_on = True

    def stop_camera(self):
        if self.camera_event: self.camera_event.cancel(); self.camera_event = None
        if self.capture: self.capture.release(); self.capture = None
        self.camera_is_on = False
        self.ids.camera_view.texture = None

    def update_camera_feed(self, dt):
        if not self.capture: return
        ret, frame = self.capture.read()
        if not ret: return
        processed_frame = self.analyze_frame(frame)
        buf = cv2.flip(processed_frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.ids.camera_view.texture = texture

    def convert_pixel_to_lux(self, pixel_value):
        return max(0, (self.INTENSITY_SLOPE * pixel_value) + self.INTENSITY_INTERCEPT)

    def convert_lux_to_candela(self, lux_value):
        return lux_value * self.LUX_TO_CANDELA_FACTOR

    # def analyze_frame(self, frame):
    #     gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #     display_frame = frame
    #     (_minVal, _maxVal, _minLoc, maxLoc) = cv2.minMaxLoc(gray_frame)
    #     beam_center_x, beam_center_y = maxLoc
    #     roi_size = 50
    #     roi_x, roi_y = max(0, beam_center_x - roi_size // 2), max(0, beam_center_y - roi_size // 2)
    #     roi_gray = gray_frame[roi_y : roi_y + roi_size, roi_x : roi_x + roi_size]
    #     if roi_gray.size > 0:
    #         mean_pixel_val = cv2.mean(roi_gray)[0]
    #         self.current_cd = self.convert_lux_to_candela(self.convert_pixel_to_lux(mean_pixel_val))
    #         self.current_dev_h = (beam_center_x - self.REF_POINT_X) / self.PIXELS_PER_DEGREE_HORIZONTAL
    #         pixel_dev_y = self.REF_POINT_Y - beam_center_y
    #         dev_in_mm = pixel_dev_y * self.MM_PER_PIXEL_VERTICAL
    #         self.current_dev_v = (dev_in_mm / (self.TEST_DISTANCE_METERS * 1000)) * 100
    #     cv2.circle(display_frame, (self.REF_POINT_X, self.REF_POINT_Y), 10, (255, 0, 0), 2)
    #     cv2.circle(display_frame, maxLoc, 15, (0, 255, 0), 2)
    #     cv2.putText(display_frame, f"Daya: {self.current_cd:.0f} cd", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
    #     return display_frame

    def analyze_frame(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        display_frame = frame

        (frame_height, frame_width) = frame.shape[:2]
        
        search_roi_width = 450  # Misal: Lebar 300 piksel
        search_roi_height = 250 # Misal: Tinggi 200 piksel
        
        # Hitung koordinat x, y untuk ROI agar tetap di tengah
        roi_x = int((frame_width / 2) - (search_roi_width / 2))
        roi_y = int((frame_height / 2) - (search_roi_height / 2))

        # 2. Ambil hanya bagian ROI dari frame grayscale
        #    Pastikan ROI tidak keluar dari batas frame
        roi_x = max(0, roi_x)
        roi_y = max(0, roi_y)
        search_roi_gray = gray_frame[roi_y : min(roi_y + search_roi_height, frame_height), 
                                     roi_x : min(roi_x + search_roi_width, frame_width)]

        if search_roi_gray.size == 0:
            # Jika ROI gagal dibuat, kembalikan frame asli
            return frame 

        # 3. Cari titik terterang (maxLoc) HANYA di dalam ROI
        (_minVal, _maxVal, _minLoc, maxLoc_relative) = cv2.minMaxLoc(search_roi_gray)
        
        # 4. Konversi koordinat maxLoc_relative (relatif terhadap ROI) 
        #    ke koordinat global (relatif terhadap frame utama)
        beam_center_x = maxLoc_relative[0] + roi_x
        beam_center_y = maxLoc_relative[1] + roi_y
        
        # Simpan koordinat global untuk menggambar lingkaran
        maxLoc = (beam_center_x, beam_center_y) 
        
        # --- PERUBAHAN SELESAI ---

        # Kode selanjutnya (untuk averaging) tetap sama,
        # tapi sekarang 'beam_center_x/y' sudah dibatasi oleh ROI di atas.
        roi_size = 50 # Ini adalah kotak untuk averaging (tetap kotak kecil)
        roi_x_avg, roi_y_avg = max(0, beam_center_x - roi_size // 2), max(0, beam_center_y - roi_size // 2)
        
        # Ambil ROI rata-rata dari frame global
        roi_gray = gray_frame[roi_y_avg : roi_y_avg + roi_size, roi_x_avg : roi_x_avg + roi_size]
        
        if roi_gray.size > 0:
            mean_pixel_val = cv2.mean(roi_gray)[0]
            self.current_cd = self.convert_lux_to_candela(self.convert_pixel_to_lux(mean_pixel_val))
            
            # Hitung deviasi berdasarkan 'beam_center_x/y' yang sudah terbatas
            self.current_dev_h = (beam_center_x - self.REF_POINT_X) / self.PIXELS_PER_DEGREE_HORIZONTAL
            pixel_dev_y = self.REF_POINT_Y - beam_center_y
            dev_in_mm = pixel_dev_y * self.MM_PER_PIXEL_VERTICAL
            self.current_dev_v = (dev_in_mm / (self.TEST_DISTANCE_METERS * 1000)) * 100
            
        # Gambar titik referensi (biru)
        cv2.circle(display_frame, (self.REF_POINT_X, self.REF_POINT_Y), 10, (255, 0, 0), 2)
        
        # Gambar titik terterang (hijau)
        cv2.circle(display_frame, maxLoc, 15, (0, 255, 0), 2)

        # --- TAMBAHAN VISUALISASI ---
        # 5. Gambar kotak ROI pencarian (kotak hijau persegi panjang)
        cv2.rectangle(display_frame, (roi_x, roi_y), (roi_x + search_roi_width, roi_y + search_roi_height), (0, 255, 0), 2)
        # --- AKHIR TAMBAHAN ---
        
        cv2.putText(display_frame, f"Daya: {self.current_cd:.0f} cd", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
        
        return display_frame

    # PERBAIKAN: Fungsi ini sekarang hanya menghitung dan mengembalikan flag
    def _calculate_pass_fail(self, cd, dev_h, dev_v, side):
        """Menghitung dan mengembalikan flag kelulusan terpisah untuk daya dan deviasi."""
        intensity_pass = cd >= self.MIN_CANDELA_THRESHOLD
        
        horizontal_pass = False
        if side == 'kiri' and abs(dev_h) <= self.MAX_DEVIATION_LEFT_DEG:
            horizontal_pass = True
        elif side == 'kanan' and abs(dev_h) <= self.MAX_DEVIATION_RIGHT_DEG:
            horizontal_pass = True
            
        vertical_pass = abs(dev_v) <= self.MAX_VERTICAL_DEVIATION_PERCENT
        
        deviation_pass = horizontal_pass and vertical_pass
        overall_status = intensity_pass and deviation_pass

        return (1 if intensity_pass else 0, 
                1 if deviation_pass else 0, 
                1 if overall_status else 0)

    def exec_save(self):
        """Menyimpan hasil uji lampu JAUH saja, TERMASUK user yang login."""
        if not dt_no_uji:
            toast("Tidak ada data kendaraan yang dipilih.")
            return

        # Hanya ambil data dari lampu JAUH
        jk = self.test_results['jauh_kanan']
        jl = self.test_results['jauh_kiri']

        # Kumpulkan semua flag individu ke dalam satu list untuk pengecekan
        all_flags = [
            jk['intensity_flag'],
            jk['deviation_flag'],
            jl['intensity_flag'],
            jl['deviation_flag']
        ]

        # Logika baru dengan 3 status: 2 (Belum Uji), 1 (Lulus), 0 (Tidak Lulus)
        if 2 in all_flags:
            final_hlm_flag = 2
        elif all(flag == 1 for flag in all_flags):
            final_hlm_flag = 1
        else:
            final_hlm_flag = 0
        
        # PERBAIKAN 1: Dapatkan user ID dan waktu
        hlm_post = str(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))
        
        # Gunakan 'dt_id_user' (dari global) bukan 'dt_hlm_user'
        hlm_user = dt_id_user 

        try:
            screen_main = self.manager.get_screen('screen_main')
            screen_main.exec_reload_database()
            cursor = mydb.cursor()

            # PERBAIKAN 2: Pastikan query SQL menggunakan kolom 'hlm_high_...'
            # (Sesuai permintaan Anda sebelumnya untuk menyimpan lampu jauh saja)
            query = f"""
                UPDATE {TB_DATA} SET
                    hlm_high_right_value = %s, hlm_high_right_flag = %s,
                    hlm_diff_high_right_value = %s, hlm_diff_high_right_flag = %s,
                    
                    hlm_high_left_value = %s, hlm_high_left_flag = %s,
                    hlm_diff_high_left_value = %s, hlm_diff_high_left_flag = %s,
                    
                    hlm_user = %s,
                    hlm_post = %s,
                    hlm_flag = %s
                WHERE nouji = %s
            """
            
            # Values sekarang cocok dengan query
            values = (
                jk['cd'], jk['intensity_flag'], jk['dev_h'], jk['deviation_flag'],
                jl['cd'], jl['intensity_flag'], jl['dev_h'], jl['deviation_flag'],
                hlm_user,
                hlm_post,
                final_hlm_flag,
                dt_no_uji
            )
            
            cursor.execute(query, values)
            mydb.commit()
            
            toast("Data Headlamp berhasil disimpan!")
            Logger.info(f"Data headlamp (jauh) untuk nouji {dt_no_uji} berhasil disimpan oleh user ID: {hlm_user}.")
            
            # PERBAIKAN 3: Navigasi kembali ke 'screen_main', bukan 'screen_menu'
            self.manager.current = 'screen_main'

        except Exception as e:
            toast("Gagal menyimpan data ke database.")
            Logger.error(f"{self.name}: Error saat menyimpan: {e}")

    def exec_navigate_main(self):
        self.manager.current = 'screen_main'

class ScreenCalibration(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenCalibration, self).__init__(**kwargs)
        self.capture = None
        self.camera_event = None
        self.camera_is_on = False
        self.calibration_data = []
        self.current_max_val = 0
        
        # Nilai kalibrasi default
        self.INTENSITY_SLOPE = 1.0
        self.INTENSITY_INTERCEPT = 0.0
        
        Clock.schedule_once(self.delayed_init, 1)

    def delayed_init(self, dt):
        """Inisialisasi label dan gambar header/footer."""
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS

    def on_enter(self):
        """Aksi saat layar dibuka: muat konfigurasi dan nyalakan kamera."""
        self.load_calibration_values()
        self.clear_data()
        self.start_camera()
        if not self.capture:
            toast("Kamera tidak ditemukan. Kembali ke menu utama.")
            Clock.schedule_once(lambda dt: self.exec_navigate_main(), 2)

    def on_leave(self):
        """Aksi saat layar ditutup: matikan kamera."""
        self.stop_camera()

    def start_camera(self):
        """Membuka device kamera dan memulai feed."""
        if self.camera_is_on:
            return
            
        # 1. Baca ID Kamera dari Config
        try:
            config.read(config_full_path)
            camera_id = config.getint('headlamp_settings', 'camera_id', fallback=1)
        except Exception as e:
            Logger.warning(f"Gagal baca ID kamera dari config: {e}")
            camera_id = 1 # Default fallback

        # 2. Inisialisasi Kamera
        try:
            # Menggunakan CAP_DSHOW untuk performa yang lebih baik di Windows
            self.capture = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        except Exception as e:
            toast(f"Error inisialisasi kamera: {e}")
            self.capture = None

        # 3. Pengecekan Keamanan (INI YANG MEMPERBAIKI ERROR 'NoneType')
        # Kita cek dulu apakah self.capture ada isinya (tidak None), baru cek isOpened()
        if self.capture is None or not self.capture.isOpened():
            toast("Error: Tidak dapat membuka kamera (Device not found).")
            self.capture = None
            return
            
        # 4. Atur properti kamera
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self.capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0) 
        self.capture.set(cv2.CAP_PROP_AUTO_WB, 0) 

        # 5. Atur exposure awal dari slider
        try:
            initial_exposure = self.ids.exposure_slider.value
            self.capture.set(cv2.CAP_PROP_EXPOSURE, initial_exposure)
            self.ids.exposure_label.text = f"Exposure: {int(initial_exposure)}"
        except:
            pass
        
        self.camera_event = Clock.schedule_interval(self.update_camera_feed, 1.0 / 30.0)
        self.camera_is_on = True
        self.camera_is_on = True

    def stop_camera(self):
        """Menghentikan feed kamera dan melepaskan device."""
        if self.camera_event:
            self.camera_event.cancel()
            self.camera_event = None
        if self.capture:
            self.capture.release()
            self.capture = None
        self.camera_is_on = False

    def on_exposure_change(self, value):
        """Dipanggil saat slider exposure diubah."""
        if self.capture and self.camera_is_on:
            self.capture.set(cv2.CAP_PROP_EXPOSURE, value)
            self.ids.exposure_label.text = f"Exposure: {int(value)}"
            
    def update_camera_feed(self, dt):
        """Membaca frame dari kamera, memprosesnya, dan menampilkannya di UI."""
        if not self.capture or not self.camera_is_on:
            return
        
        ret, frame = self.capture.read()
        if not ret:
            Logger.warning("Gagal membaca frame dari kamera.")
            return

        processed_frame = self.analyze_frame_for_calibration(frame)
        
        # Konversi frame OpenCV ke tekstur Kivy
        buf = cv2.flip(processed_frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.ids.camera_view.texture = texture

    def load_calibration_values(self):
        """Memuat nilai slope dan intercept dari config.ini."""
        try:
            config.read(config_full_path)
            self.INTENSITY_SLOPE = float(config.get('camera_calibration', 'intensity_slope'))
            self.INTENSITY_INTERCEPT = float(config.get('camera_calibration', 'intensity_intercept'))
            toast("Konfigurasi kalibrasi dimuat.")
            Logger.info(f"{self.name}: Kalibrasi dimuat: Slope={self.INTENSITY_SLOPE}, Intercept={self.INTENSITY_INTERCEPT}")
        except (configparser.NoSectionError, configparser.NoOptionError):
            Logger.warning(f"{self.name}: Sesi [camera_calibration] tidak ditemukan. Menggunakan nilai default.")
            self.INTENSITY_SLOPE = 1.0
            self.INTENSITY_INTERCEPT = 0.0

    def convert_pixel_to_lux(self, pixel_value):
        """Mengonversi nilai piksel ke lux menggunakan slope dan intercept saat ini."""
        return max(0, (self.INTENSITY_SLOPE * pixel_value) + self.INTENSITY_INTERCEPT)

    def analyze_frame_for_calibration(self, frame):
        """Menganalisis frame di area tengah untuk mendapatkan nilai piksel dan visualisasi."""
        (frame_height, frame_width) = frame.shape[:2]
        roi_size = 250  # Ukuran kotak ROI (200x200 piksel)
        
        roi_x = int((frame_width / 2) - (roi_size / 2))
        roi_y = int((frame_height / 2) - (roi_size / 2))

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        roi_gray = gray_frame[roi_y : roi_y + roi_size, roi_x : roi_x + roi_size]

        mean_val = cv2.mean(roi_gray)[0] 
        self.current_max_val = int(mean_val)

        calibrated_lux = self.convert_pixel_to_lux(self.current_max_val)

        try:
            self.ids.live_pixel_value.text = f"Nilai Piksel Mentah: [b]{self.current_max_val}[/b]"
            self.ids.calibrated_lux_value.text = f"Lux Terkalibrasi: [b]{calibrated_lux:.2f} lx[/b]"
        except KeyError:
            pass # Mencegah error jika UI belum sepenuhnya dimuat

        # Gambar kotak ROI untuk visualisasi
        cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_size, roi_y + roi_size), (0, 255, 0), 2)
        return frame

    def add_data_point(self):
        """Menambahkan titik data baru untuk kalibrasi ulang."""
        try:
            lux_from_meter = float(self.ids.lux_meter_input.text)
            pixel_value = self.current_max_val
            self.calibration_data.append((pixel_value, lux_from_meter))
            
            log_entry = f"Data-{len(self.calibration_data)}: (Piksel: {pixel_value}, Lux: {lux_from_meter})\n"
            self.ids.data_log.text += log_entry
            toast(f"Data ke-{len(self.calibration_data)} ditambahkan.")
            self.ids.lux_meter_input.text = ""
        except ValueError:
            toast("Input dari Luxmeter harus berupa angka!")
        except Exception as e:
            toast(f"Error: {e}")

    def clear_data(self):
        """Membersihkan data kalibrasi yang sudah diinput."""
        self.calibration_data = []
        try:
            self.ids.data_log.text = ""
            self.ids.lux_meter_input.text = ""
            self.ids.result_slope.text = "Hasil Slope: -"
            self.ids.result_intercept.text = "Hasil Intercept: -"
            toast("Data dibersihkan.")
        except KeyError:
            pass

    def calculate_and_save(self):
        if len(self.calibration_data) < 2:
            toast("Data tidak cukup! Kumpulkan minimal 2 titik data.")
            return

        try:
            x_values = np.array([item[0] for item in self.calibration_data])
            y_values = np.array([item[1] for item in self.calibration_data])
            slope, intercept = np.polyfit(x_values, y_values, 1)

            # Buat objek ConfigParser BARU untuk memastikan tidak ada data lama
            local_config = configparser.ConfigParser()
            local_config.read(config_full_path) # Baca seluruh isi file yang ada

            if not local_config.has_section('camera_calibration'):
                local_config.add_section('camera_calibration')
            
            # Atur nilai baru
            local_config.set('camera_calibration', 'intensity_slope', str(slope))
            local_config.set('camera_calibration', 'intensity_intercept', str(intercept))
            current_exposure = self.ids.exposure_slider.value
            local_config.set('camera_calibration', 'exposure', str(current_exposure))

            # Tulis kembali seluruh konfigurasi ke file
            with open(config_full_path, 'w') as configfile:
                local_config.write(configfile)
            
            # Perbarui nilai internal dan UI
            self.INTENSITY_SLOPE = slope
            self.INTENSITY_INTERCEPT = intercept
            self.ids.result_slope.text = f"Hasil Slope: [b]{slope:.4f}[/b]"
            self.ids.result_intercept.text = f"Hasil Intercept: [b]{intercept:.4f}[/b]"
            
            toast("Kalibrasi baru berhasil disimpan!", duration=3)

        except PermissionError:
            toast("Gagal menyimpan: Izin ditolak. Coba jalankan sebagai administrator.")
        except Exception as e:
            toast(f"Gagal menghitung atau menyimpan: {e}")
            Logger.error(f"{self.name}: Gagal kalkulasi/simpan - {e}")

    def exec_navigate_main(self):
        """Fungsi untuk kembali ke menu utama."""
        self.manager.current = 'screen_main'

class RootScreen(ScreenManager):
    pass

class HeadlampmeterApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.on_window_resize)

    def build(self):
        global window_size_x, window_size_y
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Gray"
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.icon = 'assets/images/logo-load-app.png'
        window_size_y = Window.size[0]
        window_size_x = Window.size[1]
        self.set_dynamic_fonts(Window.size)

        LabelBase.register(
            name="Orbitron-Regular",
            fn_regular="assets/fonts/Orbitron-Regular.ttf")
        
        LabelBase.register(
            name="Draco",
            fn_regular="assets/fonts/Draco.otf")        

        LabelBase.register(
            name="Recharge",
            fn_regular="assets/fonts/Recharge.otf") 
        
        theme_font_styles.append('H1')
        self.theme_cls.font_styles["H1"] = [
            "Orbitron-Regular", 64, False, 0.15]       

        theme_font_styles.append('H2')
        self.theme_cls.font_styles["H2"] = [
            "Orbitron-Regular", 32, False, 0.15] 
        
        theme_font_styles.append('H4')
        self.theme_cls.font_styles["H4"] = [
            "Recharge", 30, False, 0.15] 

        theme_font_styles.append('H5')
        self.theme_cls.font_styles["H5"] = [
            "Recharge", 20, False, 0.15] 

        theme_font_styles.append('H6')
        self.theme_cls.font_styles["H6"] = [
            "Recharge", 16, False, 0.15] 

        theme_font_styles.append('Subtitle1')
        self.theme_cls.font_styles["Subtitle1"] = [
            "Recharge", 11, False, 0.15] 

        theme_font_styles.append('Body1')
        self.theme_cls.font_styles["Body1"] = [
            "Recharge", 10, False, 0.15] 
        
        theme_font_styles.append('Button')
        self.theme_cls.font_styles["Button"] = [
            "Recharge", 9, False, 0.15] 

        theme_font_styles.append('Caption')
        self.theme_cls.font_styles["Caption"] = [
            "Recharge", 8, False, 0.15]       
        
        Window.fullscreen = 'auto'
        Builder.load_file('main.kv')
        return RootScreen()

    def on_window_resize(self, window, width, height):
        Logger.info(f"Window size: {width}x{height}")
        self.set_dynamic_fonts((width, height))
        self.refresh_all_fonts()

    def refresh_all_fonts(self):
        if hasattr(self, 'root') and hasattr(self.root, 'screens'):
            for screen in self.root.screens:
                self.refresh_fonts(screen)

    def refresh_fonts(self, widget):
        from kivymd.uix.label import MDLabel
        if isinstance(widget, MDLabel):
            original_style = widget.font_style
            temp_style = "Body1" if original_style != "Body1" else "H6"
            widget.font_style = temp_style
            widget.font_style = original_style
        if hasattr(widget, 'children'):
            for child in widget.children:
                self.refresh_fonts(child)

    def set_dynamic_fonts(self, size):
        try:
            screen_size_x = Window.system_size[0]
            screen_size_y = Window.system_size[1]
        except AttributeError:
            screen_size_x = Window._get_system_size()[0]
            screen_size_y = Window._get_system_size()[1]
        font_size_l = np.array([64, 32, 30, 20, 16, 11, 10, 9, 8])
        scale = min(screen_size_x / 1920, screen_size_y / 1080)
        font_size = np.round(font_size_l * scale, 0)
        Logger.info(f"Font resized: {font_size_l} to {font_size}")
        self.theme_cls.font_styles["H1"] = [
            "Orbitron-Regular", font_size[0], False, 0.15]
        self.theme_cls.font_styles["H2"] = [
            "Orbitron-Regular", font_size[1], False, 0.15]
        self.theme_cls.font_styles["H4"] = [
            "Recharge", font_size[2], False, 0.15]
        self.theme_cls.font_styles["H5"] = [
            "Recharge", font_size[3], False, 0.15]
        self.theme_cls.font_styles["H6"] = [
            "Recharge", font_size[4], False, 0.15]
        self.theme_cls.font_styles["Subtitle1"] = [
            "Recharge", font_size[5], False, 0.15]
        self.theme_cls.font_styles["Body1"] = [
            "Recharge", font_size[6], False, 0.15]
        self.theme_cls.font_styles["Button"] = [
            "Recharge", font_size[7], False, 0.15]
        self.theme_cls.font_styles["Caption"] = [
            "Recharge", font_size[8], False, 0.15]       

        if hasattr(self, 'root'):
            self.refresh_fonts(self.root)

if __name__ == '__main__':
    HeadlampmeterApp().run()
