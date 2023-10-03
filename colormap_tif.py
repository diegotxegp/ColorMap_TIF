import os
import rasterio
import numpy as np


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
            meta = src.meta
            nodata = meta["nodata"]
            meta["dtype"] = "uint16"
            meta["nodata"] = 0

            cotas_window = set()
            
            print(f"Leyendo...")
            for _, window in src.block_windows(1):

                #print(window)

                band = src.read(1, window=window)
                band[band == nodata] = meta["nodata"]
                band[band == np.nan] = meta["nodata"]
                band *= 1000

                cotas_window.update(band.ravel())  # Ravel convierte la matriz a una serie 1D

            
            # Lista con las cotas ordenadas de menor a mayor
            cotas_ordenadas = sorted(list(cotas_window))
            cotas_window = None
            cotas = [int(cota) for cota in cotas_ordenadas if ~np.isnan(cota)]
            cotas_ordenadas = None
            cotas = cotas[1:] # Suprimimos el nodata value

            tonalidades = generar_colores_graduales(len(cotas))

            color_dict = {}
            for i, cota in enumerate(cotas):
                color_dict[cota] = tonalidades[i]

            cotas = None
            tonalidades = None

            # Guarda la banda editada como un nuevo archivo TIFF
            with rasterio.open(out_tif, 'w', **meta) as dst:

                print(f"Escribiendo...")
                for _, window in src.block_windows(1):

                    #print(window)

                    band = src.read(1, window=window)
                    band[band == nodata] = meta["nodata"]
                    band[band == np.nan] = meta["nodata"]
                    band *= 1000

                    dst.write(band, 1, window = window)
                    dst.write_colormap(1, color_dict)


            print("¡Mapa coloreado!")

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
    carpeta_inicial = r"C:\Users\gprietod\Desktop\Rasters_CFCC"
    carpeta_coloreada = r"C:\Users\gprietod\Desktop\Mapa_Rasters"
###########################################################################################################################
    
    colormap_tif(carpeta_inicial, carpeta_coloreada)
    print("Todos los mapas han sido coloreados.")