PAGE_SIZE_SM=20
PAGE_SIZE_LG=50

HOME_TEXT = '''
This is a demo dashboard. Note that this dashboard and its data preprocessing are not meant to be perfect. It just serves as a reference and basis.

These are the applications analysed:
'''

SIDEBAR_STYLE = {
	"position": "fixed",
	"top": 56,
	"left": 0,
	"bottom": 0,
	"width": "16rem",
	"height": "100%",
	"z-index": 1,
	"overflow-x": "hidden",
	"transition": "all 0.5s",
	"padding": "0.5rem 1.8rem",
	"background-color": "#f8f9fa",
}

SIDEBAR_HIDDEN = {
	"position": "fixed",
	"top": 56,
	"left": "-16rem",
	"bottom": 0,
	"width": "16rem",
	"height": "100%",
	"z-index": 1,
	"overflow-x": "hidden",
	"transition": "all 0.5s",
	"padding": "0.5rem 1.8rem",
	"background-color": "#f8f9fa",
}

CONTENT_STYLE_PARTIAL = {
	"transition": "margin-left .5s",
	"margin": "1.7rem 1.9rem 1.7rem 17.9rem",
}

CONTENT_STYLE_FULL = {
	"transition": "margin-left .5s",
	"margin": "1.7rem 1.9rem",
}

DATATABLE_TITLE_STYLE = {
	'fontSize':18,
	'font-family':'Arial',
	'color':'#444'}

INPUT_NUMBER_STYLE = {
	'width':'250px',
	'fontSize':12,
	'font-family':'sans-serif',
	'float':'right',
}

CELL_STYLE = {
	'textAlign':'left',
	'fontSize':10,
	'font-family':'sans-serif',
}

operators = [
	['contains ']
]