import sqlite3
import matplotlib

matplotlib.use('Agg')  # Matplotlib arka planını, pencere göstermeden dosyaları bellekte kaydetmek için ayarlama
import matplotlib.pyplot as plt
import cartopy.crs as ccrs  # Harita projeksiyonlarıyla çalışmamızı sağlayacak modülü içe aktarma

class DB_Map():
    def __init__(self, database):
        self.database = database  # Veri tabanı yolunu belirleme

    def create_user_table(self):
        conn = sqlite3.connect(self.database)  # Veri tabanına bağlanma
        with conn:
            # Kullanıcı şehirlerini depolamak için bir tablo oluşturma (eğer yoksa)
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()  # Değişiklikleri onaylama

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Veri tabanında şehir adına göre sorgulama yapma
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                # Şehri kullanıcının şehir listesine ekleme
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1  # İşlemin başarılı olduğunu belirtme
            else:
                return 0  # Şehir bulunamadı

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Kullanıcının tüm şehirlerini seçme
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities  # Kullanıcının şehir listesini döndürme

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Şehrin adına göre koordinatlarını alma
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates  # Şehrin koordinatlarını döndürme

    def create_graph(self, path, cities):
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()
        for city in cities:
            try:
                lat, lng = self.get_coordinates(city)
                plt.plot([lng],[lat], color="orange", marker=".", transform=ccrs.PlateCarree())
                plt.text(lng + 3, lat - 12, city, horizontalalignment='right', transform=ccrs.PlateCarree())
                plt.savefig(path)
                plt.show()
                plt.close()
            except:
                print("Tüh")
        plt.show()

    def draw_distance(self, city1, city2):
        coords1 = self.get_coordinates(city1)
        coords2 = self.get_coordinates(city2)

        if coords1 and coords2:
            lat1, lng1 = coords1
            lat2, lng2 = coords2

            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.stock_img()

            # Şehir noktalarını ve çizgiyi çiz
            plt.plot([lng1, lng2], [lat1, lat2], color="red", marker="o", transform=ccrs.PlateCarree())

            # Haritayı kaydet
            plt.savefig("distance.png")
            plt.close()
        else:
            print("Şehir'ler bulunamadı.")


if __name__ == "__main__":
    m = DB_Map("database.db")  # Veri tabanıyla etkileşime geçecek bir nesne oluşturma
    m.create_user_table()   # Kullanıcı şehirleri tablosunu oluşturma (eğer zaten yoksa)
    m.create_graph("city.png","Tokyo")
