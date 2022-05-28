import matplotlib.pyplot as plt             # pip install matplotlib
from matplotlib import font_manager, rc

font_path = "C:/Windows/Fonts/malgun.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rc("font", family=font_name)

data = [1,2,3]
label = ["Good", "Bad", "Normal"]
plt.pie(data, labels=label, autopct="%d%%")
plt.axis("equal")
plt.legend(label, loc="lower left")
plt.show()