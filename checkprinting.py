from fpdf import FPDF  # pip install fpdf2
import inflect

# Quickbooks Check
check_measurements = {
    # Section 1
    "date": {"x": 6.875, "y": 0.75, "w": 1.125, "h": 0.25},
    "payee": {"x": 1.25, "y": 1.2, "w": 5.5, "h": 0.25},
    "numeric_amount": {"x": 6.875, "y": 1.2, "w": 1.125, "h": 0.25},
    "text_amount": {"x": 2, "y": 1.575, "w": 7.125, "h": 0.25},
    "payee1": {"x": 1.25, "y": 2, "w": 5.5, "h": 0.25},
    "memo": {"x": 1.25, "y": 2.5, "w": 2, "h": 0.25},
    # Section 2
    "date_2": {"x": 6.875, "y": 3.75, "w": 1.125, "h": 0.25},
    "payee_2": {"x": 1.25, "y": 4.2, "w": 5.5, "h": 0.25},
    "numeric_amount_2": {"x": 6.875, "y": 4.2, "w": 1.125, "h": 0.25},
    "text_amount_2": {"x": 2, "y": 4.575, "w": 7.125, "h": 0.25},
    "payee1_2": {"x": 1.25, "y": 5, "w": 5.5, "h": 0.25},
    "memo_2": {"x": 1.25, "y": 5.5, "w": 2, "h": 0.25},
    # Section 3
    "date_3": {"x": 6.875, "y": 6.75, "w": 1.125, "h": 0.25},
    "payee_3": {"x": 1.25, "y": 7.2, "w": 5.5, "h": 0.25},
    "numeric_amount_3": {"x": 6.875, "y": 7.2, "w": 1.125, "h": 0.25},
    "text_amount_3": {"x": 2, "y": 7.575, "w": 7.125, "h": 0.25},
    "payee1_3": {"x": 1.25, "y": 8, "w": 5.5, "h": 0.25},
    "memo_3": {"x": 1.25, "y": 8.5, "w": 2, "h": 0.25},
}

normal_font = {"face": "Helvetica", "size": 12}
small_font = {"face": "Helvetica", "size": 10}

capitalization = str.capitalize


def set_measurements(m):
    """Sets check measurements to m, returns the old measurements"""
    global check_measurements
    old = check_measurements
    check_measurements = m
    return old


def set_fonts(normal, small):
    """Sets fonts to normal and small, returns the old fonts as a tuple"""
    global normal_font, small_font
    old = (normal_font, small_font)
    normal_font, small_font = normal, small
    return old


def set_capitalization(f):
    """sets capitalization to the function f, returns the old function"""
    global capitalization
    old = capitalization
    capitaliztion = f
    return old


def makepdf(payee, amount, date, memo="", address=""):
    """Return an FPDF object that fills out a pre-printed check.
    Output is based on the measurements in the check_measurements global,
    normal_font and small_font, and using the capitalization function.
    """
    # Initialize inflect engine
    p = inflect.engine()

    def mkcell(m, txt, extend=False, ch="-"):
        pdf.set_xy(m["x"], m["y"])
        tw = pdf.get_string_width(txt)
        cw = m["w"]
        if tw > cw:
            pdf.set_stretching(100.0 * cw / tw)
        if extend and cw > tw:
            dw = pdf.get_string_width(ch)
            n = int((cw - tw) / dw)
            txt = txt + (ch * n)
        pdf.cell(m["w"], m["h"], txt)
        pdf.set_stretching(100.0)

    def small():
        pdf.set_font(small_font["face"], size=small_font["size"])

    def normal():
        pdf.set_font(normal_font["face"], size=normal_font["size"])

    pdf = FPDF(orientation="P", unit="in", format="Letter")
    pdf.add_page()
    small()
    pdf.set_margins(0, 0, 0)

    numeric_amount = "***${:,.2f}".format(amount)

    # Split the amount into dollars and cents
    dollars, cents = divmod(round(amount * 100), 100)

    # Convert dollars to words
    dollars_in_words = p.number_to_words(dollars, andword="")

    # Format the result
    check_format = f"{dollars_in_words.capitalize()} and {cents:02d}/100 Dollars"

    mkcell(check_measurements["date"], date)
    mkcell(check_measurements["payee"], payee)
    mkcell(check_measurements["payee1"], payee)
    mkcell(check_measurements["numeric_amount"], numeric_amount)
    mkcell(check_measurements["text_amount"], check_format)
    mkcell(check_measurements["memo"], memo)

    mkcell(check_measurements["date_2"], date)
    mkcell(check_measurements["payee_2"], payee)
    mkcell(check_measurements["payee1_2"], payee)
    mkcell(check_measurements["numeric_amount_2"], numeric_amount)
    mkcell(check_measurements["text_amount_2"], check_format)
    mkcell(check_measurements["memo_2"], memo)

    mkcell(check_measurements["date_3"], date)
    mkcell(check_measurements["payee_3"], payee)
    mkcell(check_measurements["payee1_3"], payee)
    mkcell(check_measurements["numeric_amount_3"], numeric_amount)
    mkcell(check_measurements["text_amount_3"], check_format)
    mkcell(check_measurements["memo_3"], memo)

    # Process Address
    # alines = address.split("\n")

    # am = check_measurements["address"]
    # pdf.set_xy(am["x"], am["y"])
    # for txt in alines:
    #     pdf.cell(am["w"], am["h"], txt, ln=2)

    return pdf
