import os
import requests
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle

FIREBASE_URL = "https://ciss-efe78-default-rtdb.europe-west1.firebasedatabase.app/dakikalar"
KULLANICI_DOSYASI = "kullanici_bilgisi.txt"

class DakikaKart(BoxLayout):
    """Dakika Kartı (Örn: 12:35)"""
    def __init__(self, zaman_str, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 45
        self.padding = [10, 5, 10, 5]

        self.zaman_lbl = Label(text=zaman_str, font_size='15sp', bold=True, size_hint_x=0.35, halign='left')
        self.zaman_lbl.bind(size=self.zaman_lbl.setter('text_size'))

        self.durum_lbl = Label(text="Boş", font_size='13sp', size_hint_x=0.65, halign='right', color=(0.5, 0.5, 0.5, 1))
        self.durum_lbl.bind(size=self.durum_lbl.setter('text_size'))

        self.add_widget(self.zaman_lbl)
        self.add_widget(self.durum_lbl)

        with self.canvas.before:
            self.bg_color = Color(0.16, 0.16, 0.2, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
        self.bind(pos=self.güncelle_geometri, size=self.güncelle_geometri)

    def güncelle_geometri(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def stil_güncelle(self, kirmizi, mavi):
        if kirmizi and mavi:
            self.bg_color.rgb = (0.5, 0.15, 0.6) # Mor
            self.durum_lbl.text = "✓ Boran & Burak (İkiniz)"
            self.durum_lbl.color = (1, 0.8, 1, 1)
        elif kirmizi:
            self.bg_color.rgb = (0.75, 0.15, 0.2) # Kırmızı
            self.durum_lbl.text = "● Boran (Kırmızı)"
            self.durum_lbl.color = (1, 0.8, 0.8, 1)
        elif mavi:
            self.bg_color.rgb = (0.1, 0.4, 0.75) # Mavi
            self.durum_lbl.text = "● Burak (Mavi)"
            self.durum_lbl.color = (0.8, 0.9, 1, 1)
        else:
            self.bg_color.rgb = (0.16, 0.16, 0.2)
            self.durum_lbl.text = "Boş"
            self.durum_lbl.color = (0.5, 0.5, 0.5, 1)


class AnaEkran(Screen):
    """24 Saatin Izgara Halinde Listelendiği Ekran"""
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Üst Buton
        self.btn_isaretle = Button(
            text="Şu Anki Dakikayı İşaretle",
            font_size='16sp',
            bold=True,
            size_hint=(1, 0.12),
            background_normal=''
        )
        self.btn_isaretle.bind(on_press=self.app_ref.dakika_isaretle)
        layout.add_widget(self.btn_isaretle)

        # 2 Sütunlu Saat Izgarası
        scroll = ScrollView(size_hint=(1, 0.88))
        self.grid = GridLayout(cols=2, spacing=10, size_hint_y=None, padding=5)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        self.saat_butonlari = {}
        for saat in range(24):
            btn = Button(
                text=f"Saat {saat:02d}:00\n(0/60 Dolu)",
                font_size='15sp',
                bold=True,
                size_hint_y=None,
                height=70,
                halign='center',
                valign='middle',
                background_normal='',
                background_color=(0.22, 0.24, 0.3, 1)
            )
            btn.bind(on_press=lambda inst, s=saat: self.app_ref.saat_detayina_git(s))
            self.saat_butonlari[saat] = btn
            self.grid.add_widget(btn)

        scroll.add_widget(self.grid)
        layout.add_widget(scroll)
        self.add_widget(layout)


class DetayEkrani(Screen):
    """Seçilen Saatin 60 Dakikasının Gösterildiği Ekran"""
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.mevcut_saat = 0

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Üst Bar (Geri Butonu + Başlık)
        ust_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)
        
        btn_geri = Button(
            text="← Geri",
            font_size='15sp',
            bold=True,
            size_hint=(0.3, 1),
            background_normal='',
            background_color=(0.3, 0.35, 0.4, 1)
        )
        btn_geri.bind(on_press=self.geri_don)

        self.lbl_baslik = Label(text="Saat 00:00 Detayı", font_size='16sp', bold=True, size_hint=(0.7, 1))

        ust_bar.add_widget(btn_geri)
        ust_bar.add_widget(self.lbl_baslik)
        self.layout.add_widget(ust_bar)

        # 60 Dakikalık Liste
        scroll = ScrollView(size_hint=(1, 0.9))
        self.box_dakikalar = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.box_dakikalar.bind(minimum_height=self.box_dakikalar.setter('height'))

        self.dakika_kartlari = {}
        for dk in range(60):
            kart = DakikaKart(zaman_str="00:00")
            self.dakika_kartlari[dk] = kart
            self.box_dakikalar.add_widget(kart)

        scroll.add_widget(self.box_dakikalar)
        self.layout.add_widget(scroll)
        self.add_widget(self.layout)

    def saat_ayarla(self, saat):
        self.mevcut_saat = saat
        self.lbl_baslik.text = f"Saat {saat:02d}:00 Dilimi"
        for dk in range(60):
            zaman_str = f"{saat:02d}:{dk:02d}"
            self.dakika_kartlari[dk].zaman_lbl.text = zaman_str

    def geri_don(self, instance):
        self.manager.current = 'ana_ekran'


class CisTakibiApp(App):
    def build(self):
        self.title = "Çiş Takibi"
        self.kullanici = self.kullanici_oku()
        self.tombala_kutlandi = False

        self.sm = ScreenManager()

        if not self.kullanici:
            self.kullanici_secim_ekrani()
        else:
            self.uygulamayi_baslat()

        return self.sm

    def kullanici_oku(self):
        if os.path.exists(KULLANICI_DOSYASI):
            with open(KULLANICI_DOSYASI, "r") as f:
                return f.read().strip()
        return None

    def kullanici_kaydet(self, rol):
        with open(KULLANICI_DOSYASI, "w") as f:
            f.write(rol)

    def kullanici_secim_ekrani(self):
        screen = Screen(name='giris')
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        lbl = Label(text="Çiş Takibi\nKim olarak giriş yapıyorsunuz?", font_size='20sp', bold=True, halign='center', size_hint=(1, 0.3))

        btn_kirmizi = Button(text="Boran (Kırmızı)", font_size='18sp', bold=True, background_normal='', background_color=(0.8, 0.2, 0.2, 1), size_hint=(1, 0.35))
        btn_kirmizi.bind(on_press=lambda x: self.rol_sec("kirmizi"))

        btn_mavi = Button(text="Burak (Mavi)", font_size='18sp', bold=True, background_normal='', background_color=(0.15, 0.45, 0.8, 1), size_hint=(1, 0.35))
        btn_mavi.bind(on_press=lambda x: self.rol_sec("mavi"))

        layout.add_widget(lbl)
        layout.add_widget(btn_kirmizi)
        layout.add_widget(btn_mavi)
        screen.add_widget(layout)

        self.sm.add_widget(screen)
        self.sm.current = 'giris'

    def rol_sec(self, rol):
        self.kullanici_kaydet(rol)
        self.kullanici = rol
        self.uygulamayi_baslat()

    def uygulamayi_baslat(self):
        self.ana_ekran = AnaEkran(app_ref=self, name='ana_ekran')
        self.detay_ekrani = DetayEkrani(app_ref=self, name='detay_ekrani')

        # Üst Buton Rengi ve Yazısı
        if self.kullanici == "kirmizi":
            self.ana_ekran.btn_isaretle.text = "Şu Anki Dakikayı İşaretle (Boran)"
            self.ana_ekran.btn_isaretle.background_color = (0.85, 0.2, 0.2, 1)
        else:
            self.ana_ekran.btn_isaretle.text = "Şu Anki Dakikayı İşaretle (Burak)"
            self.ana_ekran.btn_isaretle.background_color = (0.15, 0.5, 0.85, 1)

        self.sm.add_widget(self.ana_ekran)
        self.sm.add_widget(self.detay_ekrani)
        self.sm.current = 'ana_ekran'

        Clock.schedule_interval(self.verileri_canli_yenile, 3)

    def saat_detayina_git(self, saat):
        self.detay_ekrani.saat_ayarla(saat)
        self.verileri_canli_yenile(0)
        self.sm.current = 'detay_ekrani'

    def bildirim_goster(self, baslik, mesaj):
        popup = Popup(
            title=baslik,
            content=Label(text=mesaj, font_size='15sp', halign='center'),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def dakika_isaretle(self, instance):
        su_an = datetime.now().strftime("%H:%M")
        key = su_an.replace(':', '_')

        try:
            res = requests.get(f"{FIREBASE_URL}/{key}.json").json() or {}
        except:
            res = {}

        kirmizi_var = res.get("kirmizi", False)
        mavi_var = res.get("mavi", False)

        if self.kullanici == "kirmizi" and kirmizi_var:
            self.bildirim_goster("Bilgi", f"Zaten {su_an} dakikasını işaretlediniz!")
            return
        if self.kullanici == "mavi" and mavi_var:
            self.bildirim_goster("Bilgi", f"Zaten {su_an} dakikasını işaretlediniz!")
            return

        if self.kullanici == "kirmizi":
            kirmizi_var = True
        else:
            mavi_var = True

        data = {"kirmizi": kirmizi_var, "mavi": mavi_var}
        try:
            requests.put(f"{FIREBASE_URL}/{key}.json", json=data)
            self.bildirim_goster("Başarılı", f"✓ {su_an} dakikası işaretlendi!")
            self.verileri_canli_yenile(0)
        except Exception as e:
            print("Hata:", e)

    def verileri_canli_yenile(self, dt):
        try:
            tum_data = requests.get(f"{FIREBASE_URL}.json").json() or {}
        except:
            return

        toplam_dolu_dakika = 0

        for saat in range(24):
            saat_dolu_sayisi = 0

            for dk in range(60):
                zaman_str = f"{saat:02d}:{dk:02d}"
                key = zaman_str.replace(':', '_')

                durum = tum_data.get(key, {})
                k = durum.get("kirmizi", False)
                m = durum.get("mavi", False)

                if self.detay_ekrani.mevcut_saat == saat:
                    self.detay_ekrani.dakika_kartlari[dk].stil_güncelle(k, m)

                if k or m:
                    saat_dolu_sayisi += 1
                    toplam_dolu_dakika += 1

            self.ana_ekran.saat_butonlari[saat].text = f"Saat {saat:02d}:00\n({saat_dolu_sayisi}/60 Dolu)"

        # TOMBALA KONTROLÜ (Tüm gün = 1440 dakika)
        if toplam_dolu_dakika >= 1440 and not self.tombala_kutlandi:
            self.tombala_kutlandi = True
            self.bildirim_goster("🎉 TEBRİKLER! 🎉", "🎉 TOMBALA! 🎉\n\nTüm günün 1440 dakikası da doldu!")

if __name__ == '__main__':
    CisTakibiApp().run()