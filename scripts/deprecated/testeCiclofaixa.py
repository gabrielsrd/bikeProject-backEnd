import geopandas as gpd

# Caminho do arquivo shapefile
caminho_shapefile = "ciclovias/sad6996_ciclovia.shp"

# Carregar o shapefile usando geopandas
ciclofaixas = gpd.read_file(caminho_shapefile)

# Verificar o CRS do shapefile
print(ciclofaixas.crs)