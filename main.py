import sqlite3
from datetime import datetime
import sys
import shutil
import csv

# Import PyQt5
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog, QMessageBox, 
                             QTableWidgetItem, QInputDialog, QFileDialog,
                             QPushButton, QVBoxLayout, QAction, QMenu, QComboBox)
from PyQt5.QtGui import QValidator, QIntValidator, QDoubleValidator
from PyQt5.QtCore import Qt, QDate

# Import UI files
from main_window import Ui_MainWindow
from login_dialog import Ui_LoginDialog
from pelanggan_dialog import Ui_PelangganDialog
from order_dialog import Ui_OrderDialog
from inventory_dialog import Ui_InventoryDialog

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def init_db():
    try:
        conn = sqlite3.connect('laundry.db')
        c = conn.cursor()
        # Tabel Users
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
        try:
            c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
        except sqlite3.IntegrityError:
            pass
        # Tabel Pelanggan
        c.execute('''CREATE TABLE IF NOT EXISTS pelanggan
                     (id INTEGER PRIMARY KEY, nama TEXT, alamat TEXT, telepon TEXT, email TEXT)''')
        # Tabel Orders
        c.execute('''CREATE TABLE IF NOT EXISTS orders
                     (id INTEGER PRIMARY KEY, pelanggan_id INTEGER, tanggal TEXT, layanan TEXT, berat REAL, biaya REAL, status TEXT, FOREIGN KEY(pelanggan_id) REFERENCES pelanggan(id))''')
        # Tabel Inventory
        c.execute('''CREATE TABLE IF NOT EXISTS inventory
                     (id INTEGER PRIMARY KEY, nama TEXT, stok INTEGER, harga_beli REAL)''')
        # Tabel Pembayaran
        c.execute('''CREATE TABLE IF NOT EXISTS pembayaran
                     (id INTEGER PRIMARY KEY, order_id INTEGER, tanggal TEXT, jumlah_bayar REAL, kembalian REAL, FOREIGN KEY(order_id) REFERENCES orders(id))''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
    finally:
        conn.close()

# --- CLASS LOGIN DIALOG ---
class LoginDialog(QDialog, Ui_LoginDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.loginButton.clicked.connect(self.login)

    def login(self):
        username = self.usernameLineEdit.text().strip()
        password = self.passwordLineEdit.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Username dan password wajib diisi")
            return
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            conn.close()
            if user:
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Username atau password salah")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))

# --- CLASS PELANGGAN DIALOG ---
class PelangganDialog(QDialog, Ui_PelangganDialog):
    def __init__(self, pelanggan_id=None):
        super().__init__()
        self.setupUi(self)
        self.pelanggan_id = pelanggan_id
        self.simpanButton.clicked.connect(self.simpan)
        self.batalButton.clicked.connect(self.reject)
        if pelanggan_id:
            self.load_data()

    def load_data(self):
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            c.execute("SELECT nama, alamat, telepon, email FROM pelanggan WHERE id=?", (self.pelanggan_id,))
            data = c.fetchone()
            conn.close()
            if data:
                self.namaLineEdit.setText(data[0])
                self.alamatLineEdit.setText(data[1])
                self.teleponLineEdit.setText(data[2])
                self.emailLineEdit.setText(data[3])
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    def simpan(self):
        nama = self.namaLineEdit.text().strip()
        alamat = self.alamatLineEdit.text().strip()
        telepon = self.teleponLineEdit.text().strip()
        email = self.emailLineEdit.text().strip()
        if not nama:
            QMessageBox.warning(self, "Error", "Nama wajib diisi")
            return
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            if self.pelanggan_id:
                c.execute("UPDATE pelanggan SET nama=?, alamat=?, telepon=?, email=? WHERE id=?", (nama, alamat, telepon, email, self.pelanggan_id))
            else:
                c.execute("INSERT INTO pelanggan (nama, alamat, telepon, email) VALUES (?, ?, ?, ?)", (nama, alamat, telepon, email))
            conn.commit()
            conn.close()
            self.accept()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", str(e))

# --- CLASS ORDER DIALOG ---
class OrderDialog(QDialog, Ui_OrderDialog):
    def __init__(self, order_id=None):
        super().__init__()
        self.setupUi(self)
        self.order_id = order_id
        self.load_pelanggan()
        self.beratLineEdit.setValidator(QDoubleValidator(0.0, 1000.0, 2))
        self.beratLineEdit.textChanged.connect(self.hitung_biaya)
        self.layananComboBox.currentIndexChanged.connect(self.hitung_biaya)
        self.simpanButton.clicked.connect(self.simpan)
        self.batalButton.clicked.connect(self.reject)
        if order_id:
            self.load_data()

    def load_pelanggan(self):
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            c.execute("SELECT id, nama FROM pelanggan")
            pelanggan = c.fetchall()
            conn.close()
            self.pelangganComboBox.clear()
            for p in pelanggan:
                self.pelangganComboBox.addItem(p[1], p[0])
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    def hitung_biaya(self):
        try:
            text_berat = self.beratLineEdit.text().replace(',', '.')
            berat = float(text_berat or 0)
            layanan = self.layananComboBox.currentText()
            harga_per_kg = {'Cuci Kering': 5000, 'Setrika': 3000, 'Cuci Basah': 4000}.get(layanan, 0)
            total = berat * harga_per_kg
            self.totalBiayaLineEdit.setText(f"Rp {total}")
        except ValueError:
            self.totalBiayaLineEdit.setText("Rp 0")

    def load_data(self):
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            c.execute("SELECT pelanggan_id, layanan, berat, biaya FROM orders WHERE id=?", (self.order_id,))
            data = c.fetchone()
            conn.close()
            if data:
                index = self.pelangganComboBox.findData(data[0])
                self.pelangganComboBox.setCurrentIndex(index)
                self.layananComboBox.setCurrentText(data[1])
                self.beratLineEdit.setText(str(data[2]))
                self.totalBiayaLineEdit.setText(f"Rp {data[3]}")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    def simpan(self):
        pelanggan_id = self.pelangganComboBox.currentData()
        layanan = self.layananComboBox.currentText()
        try:
            berat = float(self.beratLineEdit.text().replace(',', '.') or 0)
            biaya = float(self.totalBiayaLineEdit.text().replace("Rp ", "") or 0)
        except:
            QMessageBox.warning(self, "Error", "Input berat/biaya tidak valid")
            return

        tanggal = datetime.now().strftime("%Y-%m-%d")
        if not pelanggan_id or berat <= 0 or not layanan:
            QMessageBox.warning(self, "Error", "Lengkapi data order")
            return
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            if self.order_id:
                c.execute("UPDATE orders SET pelanggan_id=?, tanggal=?, layanan=?, berat=?, biaya=? WHERE id=?", (pelanggan_id, tanggal, layanan, berat, biaya, self.order_id))
            else:
                c.execute("INSERT INTO orders (pelanggan_id, tanggal, layanan, berat, biaya, status) VALUES (?, ?, ?, ?, ?, 'Masuk')", (pelanggan_id, tanggal, layanan, berat, biaya))
            conn.commit()
            conn.close()
            self.accept()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", str(e))

# --- CLASS INVENTORY DIALOG ---
class InventoryDialog(QDialog, Ui_InventoryDialog):
    def __init__(self, inventory_id=None):
        super().__init__()
        self.setupUi(self)
        self.inventory_id = inventory_id
        self.stokLineEdit.setValidator(QIntValidator(0, 10000))
        self.hargaBeliLineEdit.setValidator(QDoubleValidator(0.0, 1000000.0, 2))
        self.simpanButton.clicked.connect(self.simpan)
        self.batalButton.clicked.connect(self.reject)
        if inventory_id:
            self.load_data()

    def load_data(self):
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            c.execute("SELECT nama, stok, harga_beli FROM inventory WHERE id=?", (self.inventory_id,))
            data = c.fetchone()
            conn.close()
            if data:
                self.namaLineEdit.setText(data[0])
                self.stokLineEdit.setText(str(data[1]))
                self.hargaBeliLineEdit.setText(str(data[2]))
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    def simpan(self):
        nama = self.namaLineEdit.text().strip()
        stok = int(self.stokLineEdit.text() or 0)
        harga_beli = float(self.hargaBeliLineEdit.text().replace(',', '.') or 0)
        if not nama or stok < 0:
            QMessageBox.warning(self, "Error", "Nama dan stok wajib valid")
            return
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            if self.inventory_id:
                c.execute("UPDATE inventory SET nama=?, stok=?, harga_beli=? WHERE id=?", (nama, stok, harga_beli, self.inventory_id))
            else:
                c.execute("INSERT INTO inventory (nama, stok, harga_beli) VALUES (?, ?, ?)", (nama, stok, harga_beli))
            conn.commit()
            conn.close()
            self.accept()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", str(e))

# --- CLASS MAIN WINDOW ---
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        init_db()
        
        # Set tanggal default untuk laporan (30 hari terakhir)
        from_date = QDate.currentDate().addDays(-30)
        to_date = QDate.currentDate()
        self.fromDateEdit.setDate(from_date)
        self.toDateEdit.setDate(to_date)
        
        # Menu Cetak
        self.setup_menu_cetak()
        
        # Connections
        self.actionExit.triggered.connect(sys.exit)
        self.actionAbout.triggered.connect(lambda: QMessageBox.information(self, "About", "Aplikasi Laundry v1.0"))
        
        # Dashboard
        self.refreshButton.clicked.connect(self.load_dashboard)
        
        # Pelanggan
        self.tambahPelangganButton.clicked.connect(self.tambah_pelanggan)
        self.editPelangganButton.clicked.connect(self.edit_pelanggan)
        self.hapusPelangganButton.clicked.connect(self.hapus_pelanggan)
        self.searchPelangganLineEdit.textChanged.connect(self.search_pelanggan)
        
        # Order
        self.buatOrderButton.clicked.connect(self.tambah_order)
        self.updateStatusButton.clicked.connect(self.update_status_order)
        
        # Inventory
        self.tambahStokButton.clicked.connect(self.tambah_inventory)
        self.editInventoryButton.clicked.connect(self.edit_inventory)
        self.kurangiStokButton.clicked.connect(self.kurangi_stok)
        
        # Pembayaran
        self.prosesPembayaranButton.clicked.connect(self.proses_pembayaran)
        self.cetakInvoiceButton.clicked.connect(self.cetak_invoice)
        
        # Laporan
        self.generateLaporanButton.clicked.connect(self.generate_laporan_pendapatan)
        self.eksporCsvButton.clicked.connect(self.ekspor_laporan_csv)
        self.eksporPdfButton.clicked.connect(self.cetak_laporan_pendapatan_pdf)  # Ubah ke fungsi baru
        
        # Pengaturan
        self.ubahPasswordButton.clicked.connect(self.ubah_password)
        self.backupDbButton.clicked.connect(self.backup_db)

        # Load data awal untuk report
        self.load_dashboard()
        self.load_pelanggan()
        self.load_orders()
        self.load_inventory()

    # --- SETUP MENU CETAK ---
    def setup_menu_cetak(self):
        """Setup menu untuk 7 report cetak"""
        self.menuCetak = QMenu("&Cetak", self)
        self.menubar.addMenu(self.menuCetak)
        
        # 7 Aksi cetak
        self.actionCetakDashboard = QAction("📊 Cetak Dashboard Harian", self)
        self.actionCetakDashboard.triggered.connect(self.cetak_dashboard_pdf)
        self.menuCetak.addAction(self.actionCetakDashboard)
        
        self.actionCetakPelanggan = QAction("👥 Cetak Daftar Pelanggan", self)
        self.actionCetakPelanggan.triggered.connect(self.cetak_daftar_pelanggan_pdf)
        self.menuCetak.addAction(self.actionCetakPelanggan)
        
        self.actionCetakOrder = QAction("🧾 Cetak Daftar Order", self)
        self.actionCetakOrder.triggered.connect(self.cetak_daftar_order_pdf)
        self.menuCetak.addAction(self.actionCetakOrder)
        
        self.actionCetakInventory = QAction("📦 Cetak Daftar Inventory", self)
        self.actionCetakInventory.triggered.connect(self.cetak_daftar_inventory_pdf)
        self.menuCetak.addAction(self.actionCetakInventory)
        
        self.actionCetakLaporan = QAction("💰 Cetak Laporan Pendapatan", self)
        self.actionCetakLaporan.triggered.connect(self.cetak_laporan_pendapatan_pdf)
        self.menuCetak.addAction(self.actionCetakLaporan)
        
        self.actionCetakStatus = QAction("📈 Cetak Laporan Status Order", self)
        self.actionCetakStatus.triggered.connect(self.cetak_laporan_status_order_pdf)
        self.menuCetak.addAction(self.actionCetakStatus)
        
        self.actionCetakInvoice = QAction("🧾 Cetak Invoice/Struk", self)
        self.actionCetakInvoice.triggered.connect(self.cetak_invoice)
        self.menuCetak.addAction(self.actionCetakInvoice)
        
        self.menuCetak.addSeparator()
        
        self.actionCetakSemua = QAction("🖨️ Cetak Semua Laporan", self)
        self.actionCetakSemua.triggered.connect(self.cetak_semua_laporan)
        self.menuCetak.addAction(self.actionCetakSemua)

    # --- REPORT 1: DASHBOARD HARIAN (TAMPIL) ---
    def load_dashboard(self):
        """REPORT 1: Dashboard - Order Hari Ini"""
        try:
            today = datetime.now().date().isoformat()
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            c.execute("SELECT o.id, p.nama, status, biaya, tanggal FROM orders o JOIN pelanggan p ON o.pelanggan_id = p.id WHERE tanggal=?", (today,))
            orders = c.fetchall()
            self.dashboardTable.setRowCount(len(orders))
            total = 0
            for row, order in enumerate(orders):
                for col, val in enumerate(order):
                    self.dashboardTable.setItem(row, col, QTableWidgetItem(str(val)))
                total += order[3]
            self.totalLabel.setText(f"Total Pendapatan Hari Ini: Rp {total}")
            
            # Statistik tambahan
            c.execute("SELECT COUNT(id) FROM orders WHERE tanggal=?", (today,))
            total_order = c.fetchone()[0]
            
            c.execute("SELECT COUNT(id) FROM orders WHERE status='Selesai' AND tanggal=?", (today,))
            order_selesai = c.fetchone()[0]
            
            self.statusbar.showMessage(f"Hari ini: {total_order} order, {order_selesai} selesai, Pendapatan: Rp {total}")
            conn.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    # --- REPORT 2: DAFTAR PELANGGAN (TAMPIL) ---
    def load_pelanggan(self):
        """REPORT 2: Daftar Semua Pelanggan"""
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            c.execute("SELECT * FROM pelanggan ORDER BY nama")
            pelanggan = c.fetchall()
            self.pelangganTable.setRowCount(len(pelanggan))
            for row, p in enumerate(pelanggan):
                for col, val in enumerate(p):
                    self.pelangganTable.setItem(row, col, QTableWidgetItem(str(val)))
            conn.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    def search_pelanggan(self):
        search = self.searchPelangganLineEdit.text().lower()
        for row in range(self.pelangganTable.rowCount()):
            match = False
            for col in range(self.pelangganTable.columnCount()):
                item = self.pelangganTable.item(row, col)
                if item and search in item.text().lower():
                    match = True
                    break
            self.pelangganTable.setRowHidden(row, not match)

    def tambah_pelanggan(self):
        dialog = PelangganDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.load_pelanggan()

    def edit_pelanggan(self):
        row = self.pelangganTable.currentRow()
        if row >= 0:
            pelanggan_id = int(self.pelangganTable.item(row, 0).text())
            dialog = PelangganDialog(pelanggan_id)
            if dialog.exec_() == QDialog.Accepted:
                self.load_pelanggan()
        else:
            QMessageBox.warning(self, "Error", "Pilih pelanggan dulu")

    def hapus_pelanggan(self):
        row = self.pelangganTable.currentRow()
        if row >= 0:
            pelanggan_id = int(self.pelangganTable.item(row, 0).text())
            reply = QMessageBox.question(self, "Konfirmasi", "Yakin hapus?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    conn = sqlite3.connect('laundry.db')
                    c = conn.cursor()
                    c.execute("DELETE FROM pelanggan WHERE id=?", (pelanggan_id,))
                    conn.commit()
                    conn.close()
                    self.load_pelanggan()
                except sqlite3.Error as e:
                    QMessageBox.critical(self, "Error", str(e))
        else:
            QMessageBox.warning(self, "Error", "Pilih pelanggan dulu")

    # --- REPORT 3: DAFTAR ORDER (TAMPIL) ---
    def load_orders(self):
        """REPORT 3: Daftar Semua Order"""
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            c.execute("SELECT o.id, p.nama, o.tanggal, o.status, o.biaya, o.layanan FROM orders o JOIN pelanggan p ON o.pelanggan_id = p.id ORDER BY o.tanggal DESC")
            orders = c.fetchall()
            self.orderTable.setRowCount(len(orders))
            for row, order in enumerate(orders):
                for col, val in enumerate(order):
                    self.orderTable.setItem(row, col, QTableWidgetItem(str(val)))
            conn.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    def tambah_order(self):
        dialog = OrderDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.load_orders()
            self.load_dashboard()

    def update_status_order(self):
        row = self.orderTable.currentRow()
        if row >= 0:
            order_id = int(self.orderTable.item(row, 0).text())
            status_baru, ok = QInputDialog.getItem(self, "Update Status", "Pilih status baru:", ["Masuk", "Proses", "Selesai"], 0, False)
            if ok:
                try:
                    conn = sqlite3.connect('laundry.db')
                    c = conn.cursor()
                    c.execute("UPDATE orders SET status=? WHERE id=?", (status_baru, order_id))
                    conn.commit()
                    conn.close()
                    self.load_orders()
                except sqlite3.Error as e:
                    QMessageBox.critical(self, "Error", str(e))
        else:
            QMessageBox.warning(self, "Error", "Pilih order dulu")

    # --- REPORT 4: DAFTAR INVENTORY (TAMPIL) ---
    def load_inventory(self):
        """REPORT 4: Daftar Inventory"""
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            c.execute("SELECT * FROM inventory ORDER BY nama")
            inventory = c.fetchall()
            self.inventoryTable.setRowCount(len(inventory))
            for row, i in enumerate(inventory):
                for col, val in enumerate(i):
                    self.inventoryTable.setItem(row, col, QTableWidgetItem(str(val)))
            conn.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    def tambah_inventory(self):
        dialog = InventoryDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.load_inventory()

    def edit_inventory(self):
        row = self.inventoryTable.currentRow()
        if row >= 0:
            inv_id = int(self.inventoryTable.item(row, 0).text())
            dialog = InventoryDialog(inv_id)
            if dialog.exec_() == QDialog.Accepted:
                self.load_inventory()
        else:
            QMessageBox.warning(self, "Error", "Pilih inventory dulu")

    def kurangi_stok(self):
        row = self.inventoryTable.currentRow()
        if row >= 0:
            inv_id = int(self.inventoryTable.item(row, 0).text())
            jumlah, ok = QInputDialog.getInt(self, "Kurangi Stok", "Jumlah:", 1, 1, 1000)
            if ok:
                try:
                    conn = sqlite3.connect('laundry.db')
                    c = conn.cursor()
                    c.execute("UPDATE inventory SET stok = stok - ? WHERE id=?", (jumlah, inv_id))
                    conn.commit()
                    conn.close()
                    self.load_inventory()
                except sqlite3.Error as e:
                    QMessageBox.critical(self, "Error", str(e))

    # --- REPORT 5: LAPORAN PENDAPATAN (TAMPIL) ---
    def generate_laporan_pendapatan(self):
        """REPORT 5: Laporan Pendapatan Berdasarkan Periode"""
        tgl_mulai = self.fromDateEdit.date().toString("yyyy-MM-dd")
        tgl_selesai = self.toDateEdit.date().toString("yyyy-MM-dd")
        
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            
            query = """
                SELECT tanggal, COUNT(id) as jumlah_order, SUM(biaya) as total_pendapatan
                FROM orders 
                WHERE tanggal BETWEEN ? AND ?
                GROUP BY tanggal
                ORDER BY tanggal DESC
            """
            c.execute(query, (tgl_mulai, tgl_selesai))
            data = c.fetchall()
            
            # Set header tabel
            self.laporanTable.setColumnCount(3)
            self.laporanTable.setHorizontalHeaderLabels(["Tanggal", "Jumlah Order", "Total Pendapatan"])
            
            self.laporanTable.setRowCount(len(data))
            total_pendapatan = 0
            
            for row_idx, row_data in enumerate(data):
                self.laporanTable.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))
                self.laporanTable.setItem(row_idx, 1, QTableWidgetItem(str(row_data[1])))
                
                if row_data[2]:
                    pendapatan = float(row_data[2])
                    self.laporanTable.setItem(row_idx, 2, QTableWidgetItem(f"Rp {pendapatan:,.0f}"))
                    total_pendapatan += pendapatan
                else:
                    self.laporanTable.setItem(row_idx, 2, QTableWidgetItem("Rp 0"))
            
            conn.close()
            
            if not data:
                QMessageBox.information(self, "Info", f"Tidak ada data pada rentang tanggal {tgl_mulai} sampai {tgl_selesai}")
            else:
                self.statusbar.showMessage(f"Total Pendapatan Periode: Rp {total_pendapatan:,.0f} | {tgl_mulai} - {tgl_selesai}")
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Gagal memuat laporan: {str(e)}")

    # --- REPORT 6: LAPORAN STATUS ORDER (TAMPIL) ---
    def generate_laporan_status(self):
        """REPORT 6: Laporan Order Berdasarkan Status"""
        tgl_mulai = self.fromDateEdit.date().toString("yyyy-MM-dd")
        tgl_selesai = self.toDateEdit.date().toString("yyyy-MM-dd")
        
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            
            query = """
                SELECT status, COUNT(id) as jumlah_order, SUM(biaya) as total_biaya
                FROM orders 
                WHERE tanggal BETWEEN ? AND ?
                GROUP BY status
                ORDER BY status
            """
            c.execute(query, (tgl_mulai, tgl_selesai))
            data = c.fetchall()
            
            # Set header tabel
            self.laporanTable.setColumnCount(3)
            self.laporanTable.setHorizontalHeaderLabels(["Status Order", "Jumlah Order", "Total Biaya"])
            
            self.laporanTable.setRowCount(len(data))
            
            for row_idx, row_data in enumerate(data):
                self.laporanTable.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))
                self.laporanTable.setItem(row_idx, 1, QTableWidgetItem(str(row_data[1])))
                
                if row_data[2]:
                    biaya = float(row_data[2])
                    self.laporanTable.setItem(row_idx, 2, QTableWidgetItem(f"Rp {biaya:,.0f}"))
                else:
                    self.laporanTable.setItem(row_idx, 2, QTableWidgetItem("Rp 0"))
            
            conn.close()
            self.statusbar.showMessage(f"Laporan Status Order: {tgl_mulai} - {tgl_selesai}")
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat laporan: {str(e)}")

    # --- REPORT 7: INVOICE/STRUK (CETAK) ---
    def proses_pembayaran(self):
        order_id = self.orderIdLineEdit.text().strip()
        if not order_id:
            QMessageBox.warning(self, "Input Error", "Masukkan ID Order terlebih dahulu!")
            return
            
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            
            # Cek apakah order ada dan ambil detailnya
            c.execute("SELECT o.id, p.nama, o.biaya, o.status FROM orders o JOIN pelanggan p ON o.pelanggan_id = p.id WHERE o.id=?", (order_id,))
            order = c.fetchone()
            
            if order:
                biaya = order[2]
                status_sekarang = order[3]
                
                if status_sekarang == "Selesai":
                    QMessageBox.information(self, "Info", "Order ini sudah lunas/selesai.")
                    return

                # Ambil nominal bayar dari lineEdit
                try:
                    bayar = float(self.bayarLineEdit.text().replace("Rp", "").replace(",", "").strip() or 0)
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Masukkan nominal angka yang valid!")
                    return

                if bayar < biaya:
                    QMessageBox.warning(self, "Gagal", f"Uang kurang! Total biaya adalah Rp {biaya}")
                    return
                
                kembalian = bayar - biaya
                self.kembalianLabel.setText(f"Rp {kembalian}")
                
                # Update status order dan simpan ke tabel pembayaran
                c.execute("UPDATE orders SET status='Selesai' WHERE id=?", (order_id,))
                c.execute("INSERT INTO pembayaran (order_id, tanggal, jumlah_bayar, kembalian) VALUES (?, ?, ?, ?)",
                          (order_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), bayar, kembalian))
                
                conn.commit()
                QMessageBox.information(self, "Sukses", f"Pembayaran Berhasil!\nKembalian: Rp {kembalian}")
                
                self.load_orders()
                self.load_dashboard()
                self.bayarLineEdit.clear()
                self.kembalianLabel.setText("Rp 0")
            else:
                QMessageBox.critical(self, "Error", "ID Order tidak ditemukan!")
                
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    # ============================================================
    # 7 FUNGSI CETAK PDF (REPORT YANG BISA DICETAK)
    # ============================================================

    def cetak_invoice(self):
        """REPORT 1 CETAK: Cetak Invoice/Struk Pembayaran"""
        order_id = self.orderIdLineEdit.text().strip()
        
        if not order_id:
            QMessageBox.warning(self, "Peringatan", "Silakan masukkan ID Order terlebih dahulu!")
            return

        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            query = """
                SELECT o.id, p.nama, p.telepon, o.layanan, o.berat, o.biaya, o.tanggal, o.status
                FROM orders o 
                JOIN pelanggan p ON o.pelanggan_id = p.id 
                WHERE o.id = ?
            """
            c.execute(query, (order_id,))
            data = c.fetchone()
            conn.close()

            if not data:
                QMessageBox.warning(self, "Error", f"Data untuk ID Order {order_id} tidak ditemukan!")
                return

            # Buat nama file PDF
            file_path = f"Invoice_Order_{order_id}.pdf"
            c_pdf = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter

            # Header Invoice
            c_pdf.setFont("Helvetica-Bold", 18)
            c_pdf.drawCentredString(width/2, height - 50, "LAUNDRY EXPRESS")
            c_pdf.setFont("Helvetica", 10)
            c_pdf.drawCentredString(width/2, height - 70, "Jl. Contoh No. 123, Kota Anda")
            c_pdf.drawCentredString(width/2, height - 85, "Telp: (021) 1234567")
            
            c_pdf.setFont("Helvetica-Bold", 14)
            c_pdf.drawCentredString(width/2, height - 110, "INVOICE / STRUK PEMBAYARAN")
            c_pdf.line(50, height - 120, width - 50, height - 120)
            
            # Informasi Invoice
            y = height - 150
            c_pdf.setFont("Helvetica-Bold", 12)
            c_pdf.drawString(70, y, "INFORMASI ORDER")
            c_pdf.setFont("Helvetica", 10)
            c_pdf.drawString(70, y - 20, f"No. Invoice    : LAUNDRY-{data[0]}")
            c_pdf.drawString(70, y - 35, f"Tanggal        : {data[6]}")
            c_pdf.drawString(70, y - 50, f"Status         : {data[7]}")
            
            # Informasi Pelanggan
            c_pdf.setFont("Helvetica-Bold", 12)
            c_pdf.drawString(70, y - 80, "INFORMASI PELANGGAN")
            c_pdf.setFont("Helvetica", 10)
            c_pdf.drawString(70, y - 100, f"Nama           : {data[1]}")
            c_pdf.drawString(70, y - 115, f"Telepon        : {data[2]}")
            
            # Detail Order
            c_pdf.setFont("Helvetica-Bold", 12)
            c_pdf.drawString(70, y - 145, "DETAIL ORDER")
            
            # Tabel detail
            table_y = y - 165
            c_pdf.setFont("Helvetica-Bold", 10)
            c_pdf.drawString(70, table_y, "Layanan")
            c_pdf.drawString(200, table_y, "Berat")
            c_pdf.drawString(300, table_y, "Biaya")
            
            c_pdf.line(70, table_y - 5, 400, table_y - 5)
            
            c_pdf.setFont("Helvetica", 10)
            c_pdf.drawString(70, table_y - 20, data[3])
            c_pdf.drawString(200, table_y - 20, f"{data[4]} kg")
            c_pdf.drawString(300, table_y - 20, f"Rp {data[5]:,.0f}")
            
            # Total
            c_pdf.setFont("Helvetica-Bold", 12)
            c_pdf.drawString(250, table_y - 50, "TOTAL BAYAR:")
            c_pdf.drawString(350, table_y - 50, f"Rp {data[5]:,.0f}")
            
            # Garis pemisah
            c_pdf.line(250, table_y - 55, 450, table_y - 55)
            
            # Footer
            c_pdf.setFont("Helvetica-Oblique", 9)
            c_pdf.drawCentredString(width/2, table_y - 80, "Terima kasih atas kepercayaan Anda!")
            c_pdf.drawCentredString(width/2, table_y - 95, "Struk ini sebagai bukti pembayaran yang sah")
            
            c_pdf.save()
            QMessageBox.information(self, "Sukses", f"Invoice berhasil dicetak!\nFile: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mencetak invoice: {str(e)}")

    def cetak_laporan_pendapatan_pdf(self):
        """REPORT 2 CETAK: Cetak Laporan Pendapatan ke PDF"""
        # Pastikan data sudah digenerate
        self.generate_laporan_pendapatan()
        
        if self.laporanTable.rowCount() == 0:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data laporan pendapatan!")
            return
    
        path, _ = QFileDialog.getSaveFileName(self, "Cetak Laporan Pendapatan", 
                                              "laporan_pendapatan.pdf", "PDF Files (*.pdf)")
        
        if path:
            try:
                c = canvas.Canvas(path, pagesize=letter)
                width, height = letter
                
                # Header
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(width/2, height - 50, "LAPORAN PENDAPATAN LAUNDRY")
                
                # Periode
                tgl_mulai = self.fromDateEdit.date().toString("dd-MM-yyyy")
                tgl_selesai = self.toDateEdit.date().toString("dd-MM-yyyy")
                c.setFont("Helvetica", 12)
                c.drawString(100, height - 80, f"Periode: {tgl_mulai} sampai {tgl_selesai}")
                
                # Data tabel
                y = height - 120
                c.setFont("Helvetica-Bold", 10)
                c.drawString(100, y, "Tanggal")
                c.drawString(200, y, "Jumlah Order")
                c.drawString(300, y, "Total Pendapatan")
                
                y -= 20
                c.setFont("Helvetica", 10)
                total_pendapatan = 0
                
                for row in range(self.laporanTable.rowCount()):
                    tanggal = self.laporanTable.item(row, 0).text() if self.laporanTable.item(row, 0) else ""
                    jumlah = self.laporanTable.item(row, 1).text() if self.laporanTable.item(row, 1) else ""
                    pendapatan_text = self.laporanTable.item(row, 2).text() if self.laporanTable.item(row, 2) else "Rp 0"
                    
                    c.drawString(100, y, tanggal)
                    c.drawString(200, y, jumlah)
                    c.drawString(300, y, pendapatan_text)
                    
                    # Hitung total
                    if "Rp" in pendapatan_text:
                        try:
                            angka = float(pendapatan_text.replace("Rp", "").replace(",", "").strip())
                            total_pendapatan += angka
                        except:
                            pass
                    
                    y -= 15
                
                # Total
                c.setFont("Helvetica-Bold", 12)
                c.drawString(250, y - 20, f"TOTAL: Rp {total_pendapatan:,.0f}")
                
                c.save()
                QMessageBox.information(self, "Sukses", f"Laporan pendapatan dicetak: {path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mencetak: {str(e)}")

    def cetak_daftar_pelanggan_pdf(self):
        """REPORT 3 CETAK: Cetak Daftar Pelanggan ke PDF"""
        if self.pelangganTable.rowCount() == 0:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data pelanggan!")
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Cetak Daftar Pelanggan", 
                                              "daftar_pelanggan.pdf", "PDF Files (*.pdf)")
        
        if path:
            try:
                c = canvas.Canvas(path, pagesize=letter)
                width, height = letter
                
                # Header
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(width/2, height - 50, "DAFTAR PELANGGAN LAUNDRY")
                c.setFont("Helvetica", 10)
                c.drawCentredString(width/2, height - 70, f"Jumlah: {self.pelangganTable.rowCount()} pelanggan")
                
                # Tabel
                y = height - 100
                headers = ["ID", "Nama", "Alamat", "Telepon", "Email"]
                col_positions = [50, 100, 200, 350, 450]
                
                # Header tabel
                c.setFont("Helvetica-Bold", 10)
                for i, header in enumerate(headers):
                    c.drawString(col_positions[i], y, header)
                
                y -= 20
                c.setFont("Helvetica", 9)
                
                # Data
                for row in range(self.pelangganTable.rowCount()):
                    for col in range(min(5, self.pelangganTable.columnCount())):
                        item = self.pelangganTable.item(row, col)
                        text = item.text() if item else ""
                        # Potong teks jika terlalu panjang
                        if col == 2 and len(text) > 30:  # Alamat
                            text = text[:30] + "..."
                        elif col == 4 and len(text) > 20:  # Email
                            text = text[:20] + "..."
                        
                        c.drawString(col_positions[col], y, text)
                    
                    y -= 12
                    if y < 50:  # Halaman baru
                        c.showPage()
                        y = height - 50
                        c.setFont("Helvetica", 9)
                
                c.save()
                QMessageBox.information(self, "Sukses", f"Daftar pelanggan dicetak: {path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mencetak: {str(e)}")

    def cetak_daftar_order_pdf(self):
        """REPORT 4 CETAK: Cetak Daftar Order ke PDF"""
        if self.orderTable.rowCount() == 0:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data order!")
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Cetak Daftar Order", 
                                              "daftar_order.pdf", "PDF Files (*.pdf)")
        
        if path:
            try:
                c = canvas.Canvas(path, pagesize=letter)
                width, height = letter
                
                # Header
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(width/2, height - 50, "DAFTAR ORDER LAUNDRY")
                c.setFont("Helvetica", 10)
                c.drawCentredString(width/2, height - 70, f"Total: {self.orderTable.rowCount()} order")
                
                # Tabel
                y = height - 100
                headers = ["ID", "Pelanggan", "Tanggal", "Status", "Biaya", "Layanan"]
                col_positions = [30, 80, 180, 280, 350, 430]
                
                # Header tabel
                c.setFont("Helvetica-Bold", 9)
                for i, header in enumerate(headers):
                    c.drawString(col_positions[i], y, header)
                
                y -= 15
                c.setFont("Helvetica", 8)
                
                # Data
                total_biaya = 0
                for row in range(self.orderTable.rowCount()):
                    for col in range(min(6, self.orderTable.columnCount())):
                        item = self.orderTable.item(row, col)
                        text = item.text() if item else ""
                        
                        # Potong teks jika terlalu panjang
                        if col == 1 and len(text) > 15:  # Nama pelanggan
                            text = text[:15] + "..."
                        elif col == 5 and len(text) > 12:  # Layanan
                            text = text[:12] + "..."
                        
                        c.drawString(col_positions[col], y, text)
                        
                        # Hitung total biaya
                        if col == 4 and "Rp" in text:
                            try:
                                angka = float(text.replace("Rp", "").replace(",", "").strip())
                                total_biaya += angka
                            except:
                                pass
                    
                    y -= 12
                    if y < 50:  # Halaman baru
                        c.showPage()
                        y = height - 50
                        c.setFont("Helvetica", 8)
                
                # Total biaya
                c.setFont("Helvetica-Bold", 10)
                c.drawString(350, y - 20, f"TOTAL BIAYA: Rp {total_biaya:,.0f}")
                
                c.save()
                QMessageBox.information(self, "Sukses", f"Daftar order dicetak: {path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mencetak: {str(e)}")

    def cetak_daftar_inventory_pdf(self):
        """REPORT 5 CETAK: Cetak Daftar Inventory ke PDF"""
        if self.inventoryTable.rowCount() == 0:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data inventory!")
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Cetak Daftar Inventory", 
                                              "daftar_inventory.pdf", "PDF Files (*.pdf)")
        
        if path:
            try:
                c = canvas.Canvas(path, pagesize=letter)
                width, height = letter
                
                # Header
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(width/2, height - 50, "DAFTAR INVENTORY LAUNDRY")
                
                # Statistik
                total_nilai = 0
                total_stok = 0
                for row in range(self.inventoryTable.rowCount()):
                    stok_item = self.inventoryTable.item(row, 2)
                    harga_item = self.inventoryTable.item(row, 3)
                    if stok_item and harga_item:
                        try:
                            stok = int(stok_item.text())
                            harga_text = harga_item.text().replace("Rp", "").replace(",", "").strip()
                            harga = float(harga_text) if harga_text else 0
                            total_nilai += stok * harga
                            total_stok += stok
                        except:
                            pass
                
                c.setFont("Helvetica", 10)
                c.drawCentredString(width/2, height - 70, f"Total Item: {self.inventoryTable.rowCount()}")
                c.drawCentredString(width/2, height - 85, f"Total Stok: {total_stok} | Total Nilai: Rp {total_nilai:,.0f}")
                
                # Tabel
                y = height - 120
                headers = ["ID", "Nama Barang", "Stok", "Harga Beli", "Total Nilai"]
                col_positions = [50, 100, 250, 300, 400]
                
                # Header tabel
                c.setFont("Helvetica-Bold", 10)
                for i, header in enumerate(headers):
                    c.drawString(col_positions[i], y, header)
                
                y -= 20
                c.setFont("Helvetica", 9)
                
                # Data
                for row in range(self.inventoryTable.rowCount()):
                    # ID
                    id_item = self.inventoryTable.item(row, 0)
                    c.drawString(col_positions[0], y, id_item.text() if id_item else "")
                    
                    # Nama
                    nama_item = self.inventoryTable.item(row, 1)
                    nama = nama_item.text() if nama_item else ""
                    if len(nama) > 20:
                        nama = nama[:20] + "..."
                    c.drawString(col_positions[1], y, nama)
                    
                    # Stok
                    stok_item = self.inventoryTable.item(row, 2)
                    stok = stok_item.text() if stok_item else "0"
                    c.drawString(col_positions[2], y, stok)
                    
                    # Harga
                    harga_item = self.inventoryTable.item(row, 3)
                    harga_text = harga_item.text() if harga_item else "Rp 0"
                    c.drawString(col_positions[3], y, harga_text)
                    
                    # Total Nilai
                    if stok_item and harga_item:
                        try:
                            stok_val = int(stok)
                            harga_val = float(harga_text.replace("Rp", "").replace(",", "").strip())
                            total = stok_val * harga_val
                            c.drawString(col_positions[4], y, f"Rp {total:,.0f}")
                        except:
                            c.drawString(col_positions[4], y, "Rp 0")
                    
                    y -= 15
                    if y < 50:  # Halaman baru
                        c.showPage()
                        y = height - 50
                        c.setFont("Helvetica", 9)
                
                c.save()
                QMessageBox.information(self, "Sukses", f"Daftar inventory dicetak: {path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mencetak: {str(e)}")

    def cetak_laporan_status_order_pdf(self):
        """REPORT 6 CETAK: Cetak Laporan Status Order ke PDF"""
        # Pertama generate laporan status
        self.generate_laporan_status()
        
        if self.laporanTable.rowCount() == 0:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data status order!")
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Cetak Laporan Status Order", 
                                              "laporan_status_order.pdf", "PDF Files (*.pdf)")
        
        if path:
            try:
                c = canvas.Canvas(path, pagesize=letter)
                width, height = letter
                
                # Header
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(width/2, height - 50, "LAPORAN STATUS ORDER LAUNDRY")
                
                # Periode
                tgl_mulai = self.fromDateEdit.date().toString("dd-MM-yyyy")
                tgl_selesai = self.toDateEdit.date().toString("dd-MM-yyyy")
                c.setFont("Helvetica", 12)
                c.drawString(100, height - 80, f"Periode: {tgl_mulai} sampai {tgl_selesai}")
                
                # Data tabel
                y = height - 120
                c.setFont("Helvetica-Bold", 10)
                c.drawString(100, y, "Status Order")
                c.drawString(250, y, "Jumlah Order")
                c.drawString(350, y, "Total Biaya")
                
                y -= 20
                c.setFont("Helvetica", 10)
                total_order = 0
                total_biaya = 0
                
                for row in range(self.laporanTable.rowCount()):
                    status = self.laporanTable.item(row, 0).text() if self.laporanTable.item(row, 0) else ""
                    jumlah = self.laporanTable.item(row, 1).text() if self.laporanTable.item(row, 1) else "0"
                    biaya_text = self.laporanTable.item(row, 2).text() if self.laporanTable.item(row, 2) else "Rp 0"
                    
                    c.drawString(100, y, status)
                    c.drawString(250, y, jumlah)
                    c.drawString(350, y, biaya_text)
                    
                    # Hitung total
                    total_order += int(jumlah) if jumlah.isdigit() else 0
                    if "Rp" in biaya_text:
                        try:
                            angka = float(biaya_text.replace("Rp", "").replace(",", "").strip())
                            total_biaya += angka
                        except:
                            pass
                    
                    y -= 15
                
                # Total
                c.setFont("Helvetica-Bold", 12)
                c.drawString(100, y - 20, f"TOTAL: {total_order} order")
                c.drawString(250, y - 20, f"Rp {total_biaya:,.0f}")
                
                c.save()
                QMessageBox.information(self, "Sukses", f"Laporan status order dicetak: {path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mencetak: {str(e)}")

    def cetak_dashboard_pdf(self):
        """REPORT 7 CETAK: Cetak Dashboard/Ringkasan Harian ke PDF"""
        path, _ = QFileDialog.getSaveFileName(self, "Cetak Dashboard Harian", 
                                              "dashboard_harian.pdf", "PDF Files (*.pdf)")
        
        if path:
            try:
                c = canvas.Canvas(path, pagesize=letter)
                width, height = letter
                
                # Header
                c.setFont("Helvetica-Bold", 18)
                c.drawCentredString(width/2, height - 50, "DASHBOARD HARIAN LAUNDRY")
                
                # Tanggal
                today = datetime.now().strftime("%d-%m-%Y")
                c.setFont("Helvetica", 12)
                c.drawCentredString(width/2, height - 80, f"Tanggal: {today}")
                
                # Statistik
                y = height - 120
                c.setFont("Helvetica-Bold", 14)
                c.drawString(100, y, "STATISTIK HARIAN")
                
                y -= 30
                c.setFont("Helvetica", 11)
                
                # Ambil data dari database
                conn = sqlite3.connect('laundry.db')
                cursor = conn.cursor()
                
                # Total order hari ini
                cursor.execute("SELECT COUNT(id) FROM orders WHERE tanggal=?", (datetime.now().date().isoformat(),))
                total_order = cursor.fetchone()[0] or 0
                
                # Order per status
                cursor.execute("SELECT status, COUNT(id) FROM orders WHERE tanggal=? GROUP BY status", 
                              (datetime.now().date().isoformat(),))
                status_data = cursor.fetchall()
                
                # Total pendapatan
                cursor.execute("SELECT SUM(biaya) FROM orders WHERE tanggal=?", (datetime.now().date().isoformat(),))
                total_pendapatan = cursor.fetchone()[0] or 0
                
                # Pelanggan baru hari ini
                cursor.execute("""
                    SELECT COUNT(DISTINCT p.id) 
                    FROM pelanggan p 
                    JOIN orders o ON p.id = o.pelanggan_id 
                    WHERE o.tanggal=?
                """, (datetime.now().date().isoformat(),))
                pelanggan_hari_ini = cursor.fetchone()[0] or 0
                
                conn.close()
                
                # Tampilkan statistik
                stats = [
                    ["Total Order Hari Ini", str(total_order)],
                    ["Total Pendapatan", f"Rp {total_pendapatan:,.0f}"],
                    ["Pelanggan Dilayani", str(pelanggan_hari_ini)],
                ]
                
                for label, value in stats:
                    c.drawString(100, y, f"{label}: {value}")
                    y -= 25
                
                # Status order
                y -= 10
                c.setFont("Helvetica-Bold", 12)
                c.drawString(100, y, "STATUS ORDER:")
                y -= 25
                c.setFont("Helvetica", 11)
                
                for status, jumlah in status_data:
                    c.drawString(120, y, f"• {status}: {jumlah} order")
                    y -= 20
                
                # Footer
                c.setFont("Helvetica-Oblique", 10)
                c.drawCentredString(width/2, y - 30, "Laporan otomatis dihasilkan oleh Aplikasi Laundry")
                
                c.save()
                QMessageBox.information(self, "Sukses", f"Dashboard dicetak: {path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mencetak: {str(e)}")

    # --- FUNGSI TAMBAHAN ---
    
    def cetak_semua_laporan(self):
        """Cetak semua 7 report sekaligus"""
        reply = QMessageBox.question(self, "Cetak Semua Laporan", 
                                     "Yakin ingin mencetak semua 7 laporan?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Cetak satu per satu
            self.cetak_dashboard_pdf()
            self.cetak_daftar_pelanggan_pdf()
            self.cetak_daftar_order_pdf()
            self.cetak_daftar_inventory_pdf()
            self.cetak_laporan_pendapatan_pdf()
            self.cetak_laporan_status_order_pdf()
            QMessageBox.information(self, "Selesai", "Semua laporan telah dicetak!")

    def ekspor_laporan_csv(self):
        """Ekspor laporan ke CSV"""
        if self.laporanTable.rowCount() == 0:
            QMessageBox.warning(self, "Peringatan", "Generate laporan terlebih dahulu!")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Simpan Laporan CSV", "laporan_laundry.csv", "CSV Files (*.csv)")
        
        if path:
            try:
                with open(path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    # Tulis Header
                    headers = []
                    for col in range(self.laporanTable.columnCount()):
                        headers.append(self.laporanTable.horizontalHeaderItem(col).text())
                    writer.writerow(headers)
                    
                    # Tulis Data
                    for row in range(self.laporanTable.rowCount()):
                        row_data = []
                        for col in range(self.laporanTable.columnCount()):
                            item = self.laporanTable.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                        
                QMessageBox.information(self, "Sukses", f"Laporan berhasil diekspor ke {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {str(e)}")

    def ubah_password(self):
        password_lama = self.passwordLamaLineEdit.text()
        password_baru = self.passwordBaruLineEdit.text()
        konfirmasi = self.konfirmasiLineEdit.text()
        
        if not password_lama or not password_baru or not konfirmasi:
            QMessageBox.warning(self, "Error", "Semua field harus diisi")
            return
            
        if password_baru != konfirmasi:
            QMessageBox.warning(self, "Error", "Password baru dan konfirmasi tidak cocok")
            return
            
        try:
            conn = sqlite3.connect('laundry.db')
            c = conn.cursor()
            # Cek password lama
            c.execute("SELECT * FROM users WHERE username='admin' AND password=?", (password_lama,))
            user = c.fetchone()
            
            if user:
                # Update password
                c.execute("UPDATE users SET password=? WHERE username='admin'", (password_baru,))
                conn.commit()
                QMessageBox.information(self, "Sukses", "Password berhasil diubah")
                self.passwordLamaLineEdit.clear()
                self.passwordBaruLineEdit.clear()
                self.konfirmasiLineEdit.clear()
            else:
                QMessageBox.warning(self, "Error", "Password lama salah")
                
            conn.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    def backup_db(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Backup Database", "backup_laundry.db", "DB Files (*.db)")
        if file_name:
            try:
                shutil.copy('laundry.db', file_name)
                QMessageBox.information(self, "Sukses", f"Database berhasil dibackup ke {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal backup database: {str(e)}")

# --- MAIN PROGRAM ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    init_db()
    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())