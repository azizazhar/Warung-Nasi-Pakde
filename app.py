# PERANCANGAN SISTEM INFORMASI PENGELOLAAN PENJUALAN DI WARUNG NASI SEDERHANA

import pandas as pd
import streamlit as st
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Warung Nasi Pak-de", layout="wide")

# Membuat dan Mengkoneksi database
def koneksi_db():
    return sqlite3.connect('warung_nasi.db')

conn = koneksi_db()
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS data_hidangan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        menu_daftar TEXT,
        tarif INTEGER
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transaksi_penjualan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jam TEXT,
        bayaran_total INTEGER,
        detail_unit TEXT
    )
''')
conn.commit()
conn.close()

if 'pesanan_detail' not in st.session_state:
    st.session_state.pesanan_detail = []

# Membuat Tampilan Sidebar
st.sidebar.markdown("### Pilihan Menu")

if 'tab_menu' not in st.session_state:
    st.session_state.tab_menu = "Beranda"

if st.sidebar.button("Beranda", use_container_width=True, type="primary" if st.session_state.tab_menu == "Beranda" else "secondary"):
    st.session_state.tab_menu = "Beranda"
    st.rerun()

if st.sidebar.button("Daftar Menu Hidangan", use_container_width=True, type="primary" if st.session_state.tab_menu == "Daftar Menu Hidangan" else "secondary"):
    st.session_state.tab_menu = "Daftar Menu Hidangan"
    st.rerun()
if st.sidebar.button("Pesan Makanan & Minuman", use_container_width=True, type="primary" if st.session_state.tab_menu == "Pesan Makanan & Minuman" else "secondary"):
    st.session_state.tab_menu = "Pesan Makanan & Minuman"
    st.rerun()
if st.sidebar.button("Riwayat Pesanan", use_container_width=True, type="primary" if st.session_state.tab_menu == "Riwayat Pesanan" else "secondary"):
    st.session_state.tab_menu = "Riwayat Pesanan"
    st.rerun()

pilihan_menu = st.session_state.tab_menu

# MENU 1 - BERANDA
if pilihan_menu == "Beranda":
    st.title("Selamat Datang di Warung Nasi Pak-de")
    st.write("Nikmati hidangan lezat kesukaanmu dengan harga terjangkau dan pelayanan terbaik.")
    st.image("banner_warung.png", use_container_width=True)
    st.markdown("---")

    st.subheader("Promo Spesial Hari Ini")

    # Tampilan Diskon Promo Hidangan
    diskon1, diskon2 = st.columns([1, 1])

    with diskon1:
        st.success("""
                   **Paket Hemat**
                   Soto Ayam + Es Teh Manis
                   ~~Rp 18.000~~ -> **Rp 12.000**
                   *Berlaku khusus untuk pemesanan hari ini !*
                   """)
        
    with diskon2:
        st.success("""
                   **Paket Kenyang Berdua**
                   2 Porsi Nasi Ayam Goreng + 2 Es Jeruk
                   ~~Rp 36.000~~ -> **Rp 28.000**
                   *Cocok Dinikmati bersama teman*
                   """)
    
    st.markdown("---")

    #Tambahan Teks di Bawahnya
    st.subheader("Informasi Operasional")
    ingfo1, ingfo2, ingfo3 = st.columns(3)
    ingfo1.info("Buka Jam: 09:00 - 20:00 WIB")
    ingfo2.info("Menerima Pesanan Acara/Katering")
    ingfo3.info("Gratis Refill Air Putih Khusus Makan di Tempat")

# MENU 2 - DAFTAR MENU
elif pilihan_menu == "Daftar Menu Hidangan":
    st.title("Daftar Menu Hidangan")
    st.write("Silahkan lihat daftar hidangan yang tersedia beserta rincian harga terbaru.")
    st.markdown("---")

    # Menambahkan Input Menu
    k_input, k_tabel = st.columns([1, 2])
    with k_input:
        st.subheader("Tambah Hidangan")
        with st.form("form_tambah_menu", clear_on_submit=True):
            nama_baru = st.text_input("Nama Makanan atau Minuman", placeholder="Misal: Nasi Telur")
            harga_baru = st.number_input("Harga Jual (Rp)", min_value=0, step=1000)
            tombol_simpan = st.form_submit_button("Simpan", type="primary")

            if tombol_simpan and nama_baru != "":
                conn = koneksi_db()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO data_hidangan (menu_daftar, tarif) VALUES (?, ?)", (nama_baru, harga_baru))
                conn.commit()
                conn.close()
                st.success(f"Berhasil menambahkan menu: {nama_baru}")
                st.rerun()

    # Membuat Tampilan Tabel
    with k_tabel:
        st.subheader("Menu Hidangan Yang Tersedia Saat Ini")
        conn = koneksi_db()
        dataframe_brng = pd.read_sql_query("SELECT * FROM data_hidangan", conn)
        conn.close()

        if not dataframe_brng.empty:
            for index, row in dataframe_brng.iterrows():
                mn1, mn2, mn3 = st.columns([2, 1, 1])
                mn1.write(row['menu_daftar'])
                mn2.write(f"**Rp {row['tarif']:,}**")
                if mn3.button("Hapus Menu", key=f"del_prod_{row['id']}", type="secondary"):
                    conn = koneksi_db()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM data_hidangan WHERE id = ?", (row['id'],))
                    conn.commit()
                    conn.close()
                    st.rerun()
                st.markdown("---")
        else:
            st.info("Belum ada menu hidangan yang didaftarkan.")

# MENU 3 - PESAN HIDANGAN
elif pilihan_menu == "Pesan Makanan & Minuman":
    st.title("Pesan Makanan dan Minuman")
    st.write("Pilih menu favorit Anda dan kumpulkan di dalam daftar pesanan sebelum melakukan pembayaran.")
    st.markdown("---")

    conn = koneksi_db()
    dataframe_brng = pd.read_sql_query("SELECT * FROM data_hidangan", conn)
    conn.close()

    # Memilih Makanan & Minuman
    if not dataframe_brng.empty:
        kolom_pilihan, kolom_pesanan = st.columns([1, 1.5])

        with kolom_pilihan:
            st.subheader("Pilih Hidangan Anda")
            menu_terpilih = st.selectbox("Nama Menu", dataframe_brng['menu_daftar'].tolist())
            jatah_bagian = st.number_input("Jumlah Porsi", min_value=1, step=1)

            if st.button("Tambahkan Pesanan", type="primary", use_container_width=True):
                biaya_pesanan = dataframe_brng[dataframe_brng['menu_daftar'] == menu_terpilih]['tarif'].values[0]
                biaya_total = int(biaya_pesanan * jatah_bagian)

                st.session_state.pesanan_detail.append({
                    "Menu": menu_terpilih,
                    "Porsi": jatah_bagian,
                    "Subtotal": biaya_total
                })
                st.rerun()

        with kolom_pesanan:
            st.subheader("Daftar Pesanan Yang Dipilih")

            if len(st.session_state.pesanan_detail) > 0:
                belanja_rincian = 0
                list_rincian = []

                for idx, item in enumerate(st.session_state.pesanan_detail):
                    krc1, krc2, krc3 = st.columns([2, 1, 0.5])
                    krc1.write(f"{item['Menu']} (x{item['Porsi']})")
                    krc2.write(f"Rp {item['Subtotal']:,}")

                    if krc3.button("Batal", key=f"del_item_{idx}"):
                        st.session_state.pesanan_detail.pop(idx)
                        st.rerun()

                    belanja_rincian += item['Subtotal']
                    list_rincian.append(f"{item['Menu']} ({item['Porsi']}x)")

                st.markdown("---")
                st.write(f"### Total Pembayaran: **Rp {belanja_rincian:,}**")

                # Tombol - Bayar Pesanan
                if st.button("Selesaikan Pemesanan & Bayar", type="primary", use_container_width=True):
                    nota_jadwal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    finale_detaile = ", ".join(list_rincian)

                    conn = koneksi_db()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO transaksi_penjualan (jam, bayaran_total, detail_unit) VALUES (?, ?, ?)",
                        (nota_jadwal, belanja_rincian, finale_detaile)
                    )
                    conn.commit()
                    conn.close()

                    st.session_state.pesanan_detail = []
                    st.success("Terima Kasih! Pesanan Anda berhasil diproses dan dicatat.")
                    st.rerun()
            else:
                st.info("Daftar pesanan masih kosong.")
    else:
        st.warning("Menu belum tersedia, silahkan hubungi penjual untuk menambahkan menu.")

# MENU 4 - LAPORAN RIWAYAT PESANAN
elif pilihan_menu =="Riwayat Pesanan":
    st.title("Riwayat Pesanan")
    st.write("Daftar seluruh nota transaksi pemesanan makanan yang telah selesai diproses.")
    st.markdown("---")

    conn = koneksi_db()
    dataframe_rwyt = pd.read_sql_query("SELECT * FROM transaksi_penjualan", conn)
    conn.close()

    # Membuat Tampilan Riwayat Dengan Sebuah Filter
    saring_c, ngosongin_c = st.columns([3, 1])
    with saring_c:
        pilihan_filter = st.radio("Filter Pesanan:", ["Hari Ini", "Semua Riwayat"], horizontal=True)
    with ngosongin_c:
        if st.button("Bersihkan Seluruh Catatan", type="secondary", use_container_width=True):
            conn = koneksi_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transaksi_penjualan")
            conn.commit()
            conn.close()
            st.success("Seluruh catatan riwayat telah dibersihkan!")
            st.rerun()
    st.markdown("---")

    if not dataframe_rwyt.empty:
        today = datetime.now().strftime("%Y-%m-%d")
        dataframe_rwyt['tanggal'] = dataframe_rwyt['jam'].str.slice(0, 10)

        dataframe_tmpl = dataframe_rwyt[dataframe_rwyt['tanggal'] == today] if pilihan_filter == "Hari Ini" else dataframe_rwyt
        hasil_total = dataframe_tmpl['bayaran_total'].sum()

        st.success(f"### Total Akumulasi Nilai Penjualan ({pilihan_filter}): **Rp {hasil_total:,}**")
        st.markdown("---")

        st.subheader("Daftar Catatan Transaksi")
        for index, row in dataframe_tmpl.iterrows():
            krw1, krw2, krw3 = st.columns([1, 2, 0.5])
            with krw1:
                t_jam_tgl = row['jam'].split()[1] if pilihan_filter == "Hari Ini" else row['tanggal']
                st.write(f"waktu: {t_jam_tgl}")
            with krw2:
                st.write(f"**Rp {row['bayaran_total']:,}** ➜ {row['detail_unit']}")
            with krw3:
                if st.button("Hapus", key=f"del_kas_{row['id']}", type="secondary"):
                    conn = koneksi_db()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM transaksi_penjualan WHERE id = ?", (row['id'],))
                    conn.commit()
                    conn.close()
                    st.rerun()
            st.markdown("---")
    else:
        st.info(f"Belum ada catatan transaksi untuk kategori {pilihan_filter.lower()}.")
# SELESAI....
