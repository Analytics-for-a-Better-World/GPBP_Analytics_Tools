import geopandas as gpd
import pandas as pd
import numpy as np
from datetime import datetime
import json
import requests
from shapely.geometry import Point, Polygon, MultiPolygon
from mysql.connector import connect
import math
import time
from copy import deepcopy
from tqdm import tqdm

# API tính drive-time trong thời gian bình thường của Mapbox cho phép người dùng request
# tối đa là 25 cặp toạ độ cùng 1 lúc với tối đa là 60 một phút
max_req_min = 60
max_coord_req = 25
# mọi người có thể thay đổi giá trị của token này thành chuỗi token key của mọi người trước khi chạy hệ thống
token = """pk.eyJ1IjoicGFydmF0aHlrcmlzaG5hbmsiLCJhIjoiY2tybGFoMTZwMGJjdDJybnYyemwxY3QxMSJ9.FXaVYsMF3HIzw7ZQFQPhSw"""
# trước khi chạy thì phải sửa giá trị này để tránh việc sử dụng quá số lượng cho phép
# truy cập trang https://account.mapbox.com/statistics/ để biết lượng request đã dùng
# và lượng request free còn cho phép trong tháng
remain_req_month = 100000


def random_gps(bounds: MultiPolygon, sq_size=0.01):
    """
    Hàm này dùng để tạo các giá trị ô vuông trên bản đồ
    phục vụ việc tính toán các giá trị mapping khác nhau
    :param bounds: Biến chứa giá trị đường bao của khu vực cần vẽ.
    :param sq_size: kích thước ô vuông. 1 km = 0.01
    :return: Lưu file csv chứa toạ độ của tâm các ô vuông
    """
    # tính số chữ số đằng sau dấu thập phân của kích thước hình vuông
    # để làm tròn toạ độ của đường bao
    dec_level = round(np.log10(1 / sq_size))
    # tách giá trị tối đa/tối thiểu của kinh độ và vĩ độ
    min_lon, min_lat, max_lon, max_lat = np.round(bounds.bounds, dec_level)

    # làm tròn xuống cho các giá trị tối thiểu
    min_lon -= sq_size
    min_lat -= sq_size
    # làm tròn lên cho các giá trị tối đa
    max_lon += sq_size
    max_lat += sq_size
    # tạo chuỗi giá trị kinh độ/vĩ độ nằm trong hình bao chữ nhật
    # từ các giá trị tối đa và tối thiểu của đường bao
    lon_range = np.arange(min_lon, max_lon, sq_size)
    lat_range = np.arange(min_lat, max_lat, sq_size)
    # biến chứa các cặp kinh độ/vĩ độ nằm trong đường bao
    coor_list = []
    # tạo 2 vòng lặp để lần lượt đi qua các giá trị từ 2 chuỗi
    # kinh độ và vĩ độ để xem cặp toạ độ nào nằm trong đường bao
    for x in tqdm(lon_range):
        for y in lat_range:
            # tạo 1 biến Point để sử dụng hàm kiểm tra từ thư viện
            new_coord = Point(x, y)
            # với biến đường bao, thư viện geopandas hỗ trợ
            # hàm kiểm tra xem 1 điểm Point(x,y) có nằm trong đường bao hay ko
            if bounds.contains(new_coord):
                # nếu nằm bên trong đường bao thì gắn vào biến lưu chuỗi
                coor_list.append([x, y])

    # sau khi hoàn thành việc kiểm tra các cặp toạ độ từ 2 chuỗi kinh độ/vĩ độ
    # ta tạo 1 bảng dữ liệu để lưu xuống file csv
    res_df = pd.DataFrame(coor_list)
    res_df.columns = ["Lon", "Lat"]
    # Lưu file csv
    res_df.to_csv('./Data/iso_chrone.csv', index=False)
    return


def haversine_vectorize(lon1, lat1, lon2, lat2):
    import numpy as np

    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    newlon = lon2 - lon1
    newlat = lat2 - lat1
    haver_formula = np.sin(newlat / 2.0) ** 2 + np.cos(lat1) * np.cos(
        lat2) * np.sin(newlon / 2.0) ** 2
    dist = 2 * np.arcsin(np.sqrt(haver_formula))
    km = 6367 * dist  # 6367 for distance in KM for miles use 3958
    return round(km, 2)


def open_connection():
    """
    Tạo kết nối với hệ thống CSDL của MySQL.
    Có thể thay thế nếu sử dụng hệ thống CSDL khác
    :return: biến kết nối với CSDL MySQL
    """
    mydb = connect(
        # thay đổi thông tin để kết nối tới hệ thống CSDL
        host="localhost",  # địa chỉ IP của hệ thống
        user="xxx",  # tên tài khoản đăng nhập
        password="xxx",  # password của CSDL
        database='xxx'  # tên CSDL
    )
    return mydb


def travel_time_req(source_lon, source_lat, to_list):
    """
    Hàm được thiết kế để request thông tin từ Mapbox để tính toán drive-time bằng xe ô tô
    :param source_lon: kinh độ của điểm gốc
    :param source_lat: vĩ độ của điểm gốc
    :param to_list: danh sách toạ độ các điểm đến
    :return: trả lại danh sách thời gian di chuyển từ điểm gốc tới các điểm đến theo thứ tự ban đầu
    """
    # danh sách các toạ độ có giá trị từng điểm theo dạng: (kinh độ, vĩ độ)
    # do Mapbox yêu cầu các cặp toạ độ được nối với nhau bởi dấu ;
    # và giữa kinh độ và vĩ độ của 1 cặp đc nối với nhau bởi dấu ,
    coordinate_str = str(source_lon) + ',' + str(source_lat)
    for destination in to_list:
        coordinate_str += ';' + str(destination[0]) + ',' + str(destination[1])

    # chi tiết về cấu trúc API của Mapbox của thể được xem ở đây
    # https://docs.mapbox.com/api/navigation/matrix/
    request_url = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving/"
    request_params = """?annotations=duration&sources=0&access_token="""
    request_mapbox = request_url + coordinate_str + request_params + token
    # sau khi đường dẫn đến API của Mapbox đã hoàn thiện nội dung thì sẽ gọi qua internet
    try:
        # đây là câu lệnh dùng để gọi API của Mapbox qua internet và truy xuất thông tin trả về
        request_pack = json.loads(requests.get(request_mapbox).content)

        # trong trường hợp hệ thống gọi quá nhiều request và vượt limit
        # Mapbox sẽ giới hạn lại và trả về lỗi
        # các câu lệnh phía dưới dùng để ngăn việc thông tin lỗi của Mapbox làm hỏng dữ liệu
        # và làm hỏng hệ thống đang chạy
        if 'messsage' in request_pack.keys():
            if request_pack['durations'] == "Too Many Requests":
                print('Use too many at ' + str(datetime.today()))
                return False
        # trong trường hợp API request được trả lời hoàn thiện
        # chuỗi giá trị được cắt đi điểm đầu tiên vì giá trị này luôn = 0
        # (do là cả điểm đi và điểm đến đều là điểm gốc)
        duration_minutes = request_pack['durations'][0][1:]
        return duration_minutes
    except Exception as e:
        print(e)
        return False


def record_result(res_list: tuple, dest_type='DB'):
    """
    Hàm sử dụng để ghi kết quả ra ngoài
    :param res_list: chuỗi giá trị lưu trữ kết quả để ghi:
        - Time of request: thời điểm truy vấn Mapbox
        - Coordinates: toạ độ của điểm gốc
        - min_drive: thời gian di chuyển nhanh nhất tới 1 TTYT
    :param dest_type: loại hình lưu trữ dữ liệu. Có thể là file csv hoặc là CSDL tập trung
    :return:
    """
    if dest_type == 'DB':
        mydb = open_connection()
        cursor = mydb.cursor()
        # Thay câu lệnh này với tên bảng, tên cột tương ứng trong bảng CSDL
        insert_query = """INSERT INTO isochrone(req_time, source_point, min_drive) 
                        VALUES (%s ,%s ,%s)"""
        cursor.execute(insert_query, res_list)
        mydb.commit()
        cursor.close()
        mydb.close()
    return


def return_closest_facs(source_lon, source_lat, facs_df, facs_return):
    """
    Trả danh sách top N các trung tâm y tế gần nhất theo khoảng cách haversine
    :param source_lon: kinh độ của điểm gốc
    :param source_lat: vĩ độ của điểm gốc
    :param facs_df: bảng chứa các trung tâm y tế
    :param facs_return: số trung tâm trong top N
    :return:
    """
    # copy lại bảng để tránh ảnh hưởng bảng gốc và tạo biến giá trị template
    res_df = deepcopy(facs_df)
    harv_dist = np.zeros(res_df.shape[0], dtype=float)
    # lần lượt đi qua từng trung tâm y tế và tính khoảng cách haversine
    for i in range(len(harv_dist)):
        dest_lon = res_df['Lon'].iloc[i]
        dest_lat = res_df['Lat'].iloc[i]
        harv_dist[i] = haversine_vectorize(source_lon, source_lat, dest_lon,
                                           dest_lat)
    # lưu chuỗi giá trị vào bảng giá trị
    res_df['Harversine_Dist'] = harv_dist
    # sắp xếp theo chiều tăng dần giá trị với giá trị thấp nhất ở đầu bảng
    res_df.sort_values('Harversine_Dist', inplace=True)
    res_df.reset_index(inplace=True, drop=True)
    # sửa giá trị này để loại bỏ các giá trị thừa ko sử dụng
    # giả sử trong trường hợp tính hospital efficiency thì so sánh giữa 2 bảng giống nhau
    # thì khoảng cách tối thiểu sẽ lại luôn là giữa 1 TTYT với chính nó ở bảng còn lại
    # vì vậy sẽ sửa cut_off = 1 để loại địa điểm đứng ở vị trí 0 là chính TTYT đó đi
    cut_off = 0
    return res_df.iloc[cut_off:facs_return, :]


def simulation_core(coord_pair, remain_time, req_count, facs_df: pd.DataFrame,
                    facs_return):
    """
    Hàm sắp xếp công việc so sánh khoảng cách và yêu cầu tính toán 
    thời gian di chuyển giữa 2 khu vực khác nhau
    :param coord_pair: cặp toạ độ của điểm gốc có dạng (kinh độ, vĩ độ)
    :param remain_time: thời gian đã sử dụng từ lần reset bộ đếm gần nhất
    :param req_count: số request đã sử dụng từ lần reset bộ đếm gần nhất
    :param facs_df: bảng chứa các TTYT với toạ độ và tên
    :param facs_return: số lượng TTYT mà hệ thống sẽ trích xuất
    :return:
        - final_drive_res: str of the list of the driving time from the source
                            to the 45 closest facilities
        - final_request_time: str of the list of the request time from
                                MapBox API
        - str of the coordinates for the source GPS
        - harv_dist_str: str of the list of the harvesine distances
                        from the source to 45 closest facilities
    """
    # ghi lại mốc thời gian hiện tại để giúp việc tính thời gian từ lần cuối cùng "reset"
    # bình thường thì thời gian thực hiện 1 lần truy xuất thông tin từ Mapbox và các bước khác
    # sẽ tốn ít hơn 1s (700-800ms) nên 1 phút hệ thống sẽ chạy đc nhiều hơn 60 lần requests
    # vì vậy, sau khi hệ thống chạy đủ 60 requests thì sẽ phải nghỉ 1 lúc
    # để Mapbox request cái lượt chạy cho mình. Nếu dùng google maps thì ko phải lo
    start_time = datetime.now()
    # tách chuỗi toạ độ ra kinh độ và vĩ độ
    gps_lon, gps_lat = coord_pair
    # sử dụng hàm return_closest_facs phía trên để trả ra danh sách các TTYT gần nhất
    facs_df_45 = return_closest_facs(gps_lon, gps_lat, facs_df, facs_return)
    # trích xuất chuỗi giá trị kinh độ và vĩ độ để request API Mapbox
    facs_list = facs_df_45[['Lon', 'Lat']].to_numpy().tolist()

    # chuẩn bị 1 số thông tin trước chạy vòng lặp
    final_drive_res = []
    # số toạ độ được sử dụng mỗi request sẽ bằng số toạ độ tối đa trừ 1
    # do là phải chừa 1 cặp toạ độ cho điểm gốc
    coord_per_req = max_coord_req - 1
    # số lần chạy vòng lặp sẽ bằng giá trị làm tròn lên của phép chia
    # giữa số TTYT cần trích xuất và số toạ độ dùng mỗi lần
    num_req = math.ceil(facs_return / coord_per_req)

    for i in range(num_req):
        # 2 biến start_idx và end_idx được sử dụng để ngắt danh sách TTYT thành các chuỗi
        # có size vừa với số toạ độ cho phép mỗi lần request lên Mapbox
        start_idx = i * coord_per_req
        end_idx = (i + 1) * coord_per_req
        while True:
            # nếu mà số lần request trước khi "reset" đạt ngưỡng limit của Mapbox
            # hệ thống sẽ tự nghỉ và chờ máy đếm của Mapbox reset sang phút mới
            if req_count >= max_req_min:
                time.sleep(remain_time)

            # truy xuất thông tin drive-time từ Mapbox API bằng hàm travel_time_req ở trên
            # kết quả thu về là chuỗi giá trị drive-time của điểm gốc tới các TTYT gần nhất
            queried_res = travel_time_req(gps_lon, gps_lat,
                                          facs_list[start_idx: end_idx])
            end_time = datetime.now()
            # cost_time được sử dụng để lưu lại quá trình tính toán trong 1 phút
            # để xem từ lúc reset cho đến hiện tại, hệ thống đã dùng đc bao nhiêu thời gian
            # và khi đạt đủ số request limit thì sẽ cho hệ thống ngủ
            cost_time = (end_time - start_time).total_seconds()
            # Nếu như request thành công thì sẽ ngừng vòng lặp để thoát ra ngoài xử lý
            if queried_res:
                remain_time = max(remain_time - cost_time, 0)
                break
            # trong trường hợp ko xử lý được do vượt quá limit của Mapbox
            # thì sẽ cho hệ thống ngủ với khoảng thời gian còn thiếu để đạt đủ 1 phút
            # và reset các bộ đếm về giá trị gốc
            else:
                time.sleep(remain_time)
                remain_time = 60
                req_count = 0
        # Xử lý kết quả thu về trước khi ghi vào CSDL hoặc file csv
        # đối với trường hợp Mapbox ko tìm được thông tin đường đi
        # thì sẽ thay giá trị drive-time thành 999999 để chắc chắn rằng kết quả N/A
        # ko làm ảnh hưởng tới việc tính toán các giá trị có thể thu thập thực tế
        queried_res = [999999 if x is None else x for x in queried_res]
        final_drive_res += queried_res
        # tăng số req_count để phản ánh việc request hoàn thành
        req_count += 1
    # Lấy giá trị thấp nhất từ chuỗi thu thập được và trả về hàm khác
    min_drive = min(final_drive_res)
    return min_drive, req_count, remain_time


def main():
    """
    Hàm quản lý thời gian chạy và các vấn biến liên quan
    :return: None
    """
    # biến source_df là bảng chứa các toạ độ gốc
    source_df = pd.read_csv('./Data/iso_chrone.csv')
    # biến dest_facs là bảng chứa các toạ độ điểm đến cuối
    dest_facs = pd.read_csv('./Data/stroke_facs_latest.csv')
    dest_facs = deepcopy(dest_facs[['Name_English',
                                    'longitude', 'latitude', 'pro_name_e']])
    dest_facs.columns = ['Facility_Name', 'Lon', 'Lat', 'Province']

    # Ví dụ: đối với việc lập isochrone map cho khả năng tiếp cận các TTYT hỗ trợ đột quỵ
    # thì source_df là bảng chứa toàn bộ các điểm trong Việt Nam
    # và dest_facs là danh sách các TTYT có thể hỗ trợ đột quỵ
    # đối với nhóm thực hiện tính toán hospital efficiency
    # thì có thể thay source_df thành chính danh sách các TTYT, giống như dest_facs
    # và sửa giá trị cut_off trong hàm return_closest_facs thành 1
    # đối với mỗi nhóm TTYT khác nhau thì sẽ lọc bảng theo giá trị cột tương ứng
    # ví dụ, muốn lọc các TTYT của Hà Nội thì sẽ thêm câu lệnh này:
    # dest_facs = dest_facs.where(dest_facs['Province'] == 'Ha Noi').dropna()
    # ở câu lệnh trên thì hàm .where() giúp truy xuất từ bảng gốc
    # các dòng có giá trị thoả mãn điều kiện nằm trong ()
    # điều kiện ở đây là các dòng của bảng mà có giá trị tại cột 'Province' là 'Ha Noi'
    # lưu ý là phải dùng đúng tên cột ('Province') và giá trị kiểm tra phải tồn tại
    # trong trường hợp muốn dùng nhiều hơn 1 điều kiện thì sẽ thêm and/or
    # and muốn dùng khi mà cần tất cả các điều kiện phải đồng thời được thoả mãn
    # còn or dùng khi chỉ cần 1 trong các điều kiện thoả mãn
    # ví dụ: muốn tìm các TTYT nằm trong 1 khoảng kinh độ và vĩ độ thì sẽ sử dụng and
    # dest_facs = dest_facs.where((dest_facs['Lon'] <= 123) and (dest_facs['Lon'] >= 120)).dropna()
    # còn muốn tìm các TTYT thuộc 1 danh sách các tỉnh thì sẽ sử dụng or
    # dest_facs = dest_facs.where((dest_facs['Province'] == 'Ha Noi') and (dest_facs['Province']=='Bac Ninh')).dropna()

    number_of_simulation = source_df.shape[0]
    req_count = 0
    remain_time = 60
    # giá trị này quyết định xem top N các TTYT được dùng để tìm thời gian
    # thay vì là phải tìm toàn bộ các TTYT có ở VN, để tiết kiệm chi phí/số lượt request
    # thay đổi giá trị này cho phù hợp với nhu cầu tính toán
    req_facs_num = 24

    # vòng lặp sẽ lần lượt xử lý từng dòng giá trị của bảng source_df
    # truy xuất thời gian drive-time và xử lý kết quả
    for idx in tqdm(range(number_of_simulation)):
        # trích xuất dữ liệu của bảng source_df tại dòng có thứ tự idx
        curr_pair = source_df.iloc[idx, :]
        time_of_req = datetime.today()
        # chạy hàm simulation_core để truy xuất thời gian di chuyển gần nhất
        # cho điểm có toạ độ tại dòng idx của bảng source_df
        min_drive, req_count, remain_time = simulation_core(curr_pair,
                                                            remain_time,
                                                            req_count,
                                                            dest_facs,
                                                            req_facs_num)

        start_time = datetime.now()
        source_point = str(curr_pair[0]) + ',' + str(curr_pair[1])
        # sau đó ghi giá trị lại
        record_result((time_of_req, source_point, min_drive))
        end_time = datetime.now()
        # tính toán thời gian còn thiếu cho đủ 60s để phục vụ việc reset
        remain_time -= (end_time - start_time).total_seconds()
        # các câu lệnh kiểm tra điều kiện để reset bộ đếm và kiểm tra hệ thống
        if remain_time <= 0 and req_count <= max_req_min:
            remain_time = 60
            req_count = 0
        elif req_count >= max_req_min and remain_time < 60:
            time.sleep(remain_time)
            req_count = 0
            remain_time = 60
    return


if __name__ == '__main__':
    file_name = './Data/gadm_vietnam.geojson'
    edges = gpd.read_file(file_name, driver='GeoJSON')
    random_gps(edges)

    main()
    pass
