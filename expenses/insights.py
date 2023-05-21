import io
import urllib
import base64
import matplotlib.pyplot as plt


# def generate_pie_chart(expense_data):
#     category_totals = {}
#     for category, expenses in expense_data.items():
#         category_totals[category] = sum(expenses)

#     # Create a pie chart using Matplotlib's plt.pie function
#     fig, ax = plt.subplots(figsize=(8, 8))
#     colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#ffb3e6','#c2c2f0','#ffb3b3','#c2d6d6','#f0c2c2']
#     ax.pie(category_totals.values(), labels=category_totals.keys(), autopct='%1.1f%%', startangle=90, colors=colors)
#     ax.set_title('Expense Distribution by Category')
#     ax.axis('equal')

#     buffer = io.BytesIO()
#     plt.savefig(buffer, format='png')
#     buffer.seek(0)
#     image_png = buffer.getvalue()
#     buffer.close()

#     image_uri = urllib.parse.quote(base64.b64encode(image_png).decode())

#     return 'data:image/png;base64,' + image_uri
def generate_pie_chart(expense_data):
    category_totals = {}
    for category, expenses in expense_data.items():
        category_totals[category] = sum(expenses)

    # Create a pie chart using Matplotlib's plt.pie function
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#ffb3e6','#c2c2f0','#ffb3b3','#c2d6d6','#f0c2c2']
    pie = ax.pie(category_totals.values(), labels=category_totals.keys(), autopct='%1.1f%%', startangle=90, colors=colors)
    ax.set_title('Expense Distribution by Category')
    ax.axis('equal')

    # Create a legend with the category names only
    legend_labels = [f'{category}' for category in category_totals.keys()]
    ax.legend(pie[0], legend_labels, loc='center left', bbox_to_anchor=(1, 0.5))

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    image_uri = urllib.parse.quote(base64.b64encode(image_png).decode())

    return 'data:image/png;base64,' + image_uri




def generate_line_chart(expense_data, x_values, y_values_dict):
    fig, ax = plt.subplots(figsize=(12, 8))

    for category, color in zip(y_values_dict.keys(), ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ffb3e6', '#c2c2f0', '#ffb3b3', '#c2d6d6', '#f0c2c2']):
        y_values = y_values_dict[category]
        if len(y_values) < len(x_values):
            # Pad with zeros if y_values is shorter than x_values
            y_values += [0] * (len(x_values) - len(y_values))
        ax.plot(x_values, y_values, color=color, label=category)
        ax.fill_between(x_values, y_values, alpha=0.1, color=color)

    ax.set_title('Expense Trends Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Total Amount Spent')
    ax.legend(loc='upper left')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    image_uri = urllib.parse.quote(base64.b64encode(image_png).decode())

    return 'data:image/png;base64,' + image_uri

