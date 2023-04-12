import gi
gi.require_version('Gst', '1.0')

# this is for QR support obviously
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol

def readQR( video_dev,_set = None ):
    '''
        画像キャプチャ
        VideoCaptureインスタンス生成
    '''
    cap = cv2.VideoCapture(video_dev, cv2.CAP_DSHOW)
    cap.open(video_dev)

    try:
        while cap.isOpened():
            ret, frame = cap.read()

            if ret:
                # デコード
                value = decode(frame, symbols=[ZBarSymbol.QRCODE])

                if value:
                    for qrcode in value:
                        if _set: _set[qrcode.data] = True
                        else:
                            try:
                                cv2.destroyWindow('pyzbar')
                            except cv2.error:
                                pass
                            else:
                                x, y, w, h = qrcode.rect

                                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

                                #qrimage_path = '/tmp/qrimage.png'
                                #is_written = cv2.imwrite(qrimage_path, frame)
                                #if not is_written:
                                #    print('ERROR: image could not be saved to {qrimage_path}!')
                                return qrcode.data#, qrimage_path

                        # QRコード座標
                        x, y, w, h = qrcode.rect

                        # QRコードデータ
                        #dec_inf = qrcode.data.decode('utf-8')
                        #print('QR-decode:', dec_inf)
                        #frame = cv2.putText(frame, dec_inf, (x, y-6), font, .3, (255, 0, 0), 1, cv2.LINE_AA)

                        # バウンディングボックス
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

                # 画像表示
                cv2.imshow('pyzbar', frame)


            # quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                try:
                    cv2.destroyWindow('pyzbar')
                except cv2.error:
                    pass
                break
    except KeyboardInterrupt:
        return
    finally:
        # キャプチャリソースリリース
        cap.release()


