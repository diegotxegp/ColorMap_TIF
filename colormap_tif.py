import os
import rasterio
import numpy as np

"""
Genera códigos RGBA-16bits de azul equidistantes según la cantidad que se introduzca
"""
def generar_tonalidades_de_azul(cantidad):
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser un número positivo.")

    # Calcula el espaciado entre las tonalidades de azul
    espaciado = int(65535 / (cantidad - 1))

    # Genera la lista de tonalidades de azul
    tonalidades_azul = [(0, 0, i, 65535) for i in range(0, 65536, espaciado)]

    return tonalidades_azul

"""
Genera códigos RGBA-8bits de azul equidistantes según la cantidad que se introduzca
"""
def generar_colores_graduales(num_colores):
    colores = []
    for i in range(num_colores):
        # Calcula los componentes R, G ,B y A gradualmente
        r = int(185 - (i / (num_colores - 1)) * (185 - 10))
        g = int(245 - (i / (num_colores - 1)) * (245 - 10))
        b = int(251 - (i / (num_colores - 1)) * (251 - 145))
        a = 255
        colores.append((r, g, b, a))

    return colores

"""
Colorea el mapa TIFF
"""
def color_map(in_tif, carpeta_coloreada):

    out_tif = os.path.join(carpeta_coloreada,os.path.splitext(os.path.basename(in_tif))[0]+"_cm.tif")

    if not os.path.exists(out_tif):
    
        with rasterio.open(in_tif, 'r') as src:

            band = src.read(1)
            meta = src.meta

            nodata = meta["nodata"]

            band[band == nodata] = 0
            band *= 1000

            # Lista con las cotas ordenadas de menor a mayor
            cotas_ordenadas = sorted(set(band.ravel()))  # Ravel convierte la matriz a una serie 1D
            cotas_ordenadas = [int(cota) for cota in cotas_ordenadas if ~np.isnan(cota)]

            nodata = cotas_ordenadas[0]
            cotas = cotas_ordenadas[1:] # Suprimimos el nodata value

            # Calcula los valores de cota máxima y mínima
            cota_minima = cotas_ordenadas[1]
            cota_maxima = cotas_ordenadas[-1]

            tonalidades = generar_colores_graduales(len(cotas))

            dict = {}
            for i,cota in enumerate(cotas):
                dict[cota] = tonalidades[i]

            meta["dtype"] = "uint16"
            meta["nodata"] = nodata

            # Guarda la banda editada como un nuevo archivo TIFF
            with rasterio.open(out_tif, 'w', **meta) as dst:
                dst.write(band, 1)
                dst.write_colormap(1, dict)


    return out_tif
    

"""
Busca en una carpeta y subcarpetas ficheros en formato TIFF (.tif) para posteriormente colorear según sus cotas
"""
def colormap_tif(carpeta_inicial, carpeta_coloreada):

    if not os.path.exists(carpeta_coloreada):
        os.makedirs(carpeta_coloreada)

    for root, _, files in os.walk(carpeta_inicial):
        if root != carpeta_coloreada:
            for archivo in files:
                if archivo.endswith(".tif"):
                    archivo_tif = os.path.join(root, archivo)
                    print(f"Coloreando mapa: {archivo_tif}")
                    color_map(archivo_tif, carpeta_coloreada)


if __name__ == '__main__':
#######################################  MODIFICAR AQUÍ  ##################################################################
    carpeta_inicial = r"D:\EU_Cases\Rasters_EU"
    carpeta_coloreada = r"D:\EU_Cases\ColorMap_EU"
###########################################################################################################################
    
    colormap_tif(carpeta_inicial, carpeta_coloreada)
    print("Mapas coloreados")