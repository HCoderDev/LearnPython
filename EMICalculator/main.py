import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

chart_widget = None
def calculate():
    amount = int(principal.get())
    interest = float(rate.get())/1200
    period = float(years.get())*12
    emi_value = amount * interest * (pow((1+interest),period)/(pow((1+interest),period)-1))
    emi.set('{:.2f}'.format(emi_value))
    total_payment_value = emi_value * int(years.get()) * 12
    total_interest_value = total_payment_value - principal.get()
    total_interest.set('{:.2f}'.format(total_interest_value))
    total_payment.set('{:.2f}'.format(total_payment_value))

    label = [f'Interest ({"{:.2f}".format(total_interest_value)})', f'Principal ({principal.get()})']
    value_contrib = [total_interest_value,principal.get()]
    fig = Figure()  # create a figure object
    ax = fig.add_subplot(111)  # add an Axes to the figure

    ax.pie(value_contrib, radius=1, labels=label, autopct='%0.2f%%', shadow=False, )
    global chart_widget

    if chart_widget is not None:
        chart_widget.pack_forget()

    final_chart = FigureCanvasTkAgg(fig, frameChartsLT)
    chart_widget = final_chart.get_tk_widget()
    chart_widget.pack()


main_window = tk.Tk()
main_window.title('EMI Calculator')
main_window.geometry("")
tk.Label(main_window, text='Amount',padx=10,pady=10).grid(row=0)
tk.Label(main_window, text='Interest',padx=10,pady=10).grid(row=1)
tk.Label(main_window, text='Tenure',padx=10,pady=10).grid(row=2)
tk.Button(main_window,text='Calculate',command=calculate,padx=10,pady=10).grid(row=3,columnspan=2)
tk.Label(main_window, text='EMI',padx=10,pady=10).grid(row=4,columnspan=2)

tk.Label(main_window, text='Total Interest',padx=10,pady=10).grid(row=6,columnspan=2)

tk.Label(main_window, text='Total Amount',padx=10,pady=10).grid(row=8,columnspan=2)

principal = tk.IntVar(main_window)
rate = tk.StringVar(main_window)
years = tk.StringVar(main_window)
emi = tk.StringVar(main_window)
total_interest = tk.StringVar(main_window)
total_payment = tk.StringVar(main_window)
emi.set(0)
total_interest.set(0)
total_payment.set(0)
tk.Label(main_window, textvariable=emi,font=("Arial", 16),padx=10,pady=10).grid(row=5,columnspan=2)
tk.Label(main_window, textvariable=total_interest,font=("Arial", 16),padx=10,pady=10).grid(row=7,columnspan=2)
tk.Label(main_window, textvariable=total_payment,font=("Arial", 16),padx=10,pady=10).grid(row=9,columnspan=2)
tk.Entry(main_window,textvariable=principal).grid(row=0, column=1)
tk.Entry(main_window,textvariable=rate).grid(row=1, column=1)
tk.Entry(main_window,textvariable=years).grid(row=2, column=1)
frameChartsLT = tk.Frame(main_window)
frameChartsLT.grid(row=1,column=2,rowspan=10)
main_window.mainloop()