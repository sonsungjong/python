import matplotlib.pyplot as plt

from matplotlib import font_manager, rc
font_path = "C:\\Windows\\Fonts\\H2GTRE.TTF"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

data = [8,17,0,11,6,21,16,6,17,11,7,9,6,13,12,16,3,14,13,12]

plt.title("히스토그램")
plt.xlabel("값")
plt.ylabel("주기")
plt.hist(data)
plt.show()



# python -m pip install -U pip
# python -m pip install -U matplotlib