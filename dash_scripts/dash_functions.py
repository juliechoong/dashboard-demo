import plotly.express as px
import plotly.graph_objects as go

from dash_scripts.dash_style import operators

##############################################################################

def table_info(dff, page, size):
	if len(dff) % size:
		total_page = len(dff)//size+1
	else:
		total_page = len(dff)//size
	
	term1 = 'page' if total_page == 1 else 'pages'
	term2 = 'result' if len(dff) == 1 else 'results'
	
	return '{:,d} {} | {:,} {}'.format(total_page, term1, len(dff), term2)


def multi_sort(dff, sort_by):
	if len(sort_by):
		dff = dff.sort_values(
			[col['column_id'] for col in sort_by],
			ascending=[
				col['direction'] == 'asc'
				for col in sort_by
			],
			inplace=False
		)
	return dff


def split_filter(filter_part):
	for operator_type in operators:
		for operator in operator_type:
			if operator in filter_part:
				name_part, value_part = filter_part.split(operator, 1)
				col_name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

				value_part = value_part.strip()
				v0 = value_part[0]
				if (col_name == 'date') or (col_name == 'version_lvl2'):
					value = value_part
				else:
					try:
						value = float(value_part)
					except ValueError:
						value = value_part
				
				if isinstance(value, str):
					value = value.lower()

				return col_name, operator_type[0].strip(), value

	return [None] * 3


def search_filter_sm(filter, df):
	dff = df
	filtering_expressions = filter.split(' && ')
	
	for filter_part in filtering_expressions:
		col_name, operator, filter_value = split_filter(filter_part)

		# if there is search input
		if operator == 'contains':
			if isinstance(filter_value, float):
				dff = dff[dff[col_name]==float(filter_value)]
			else:
				df_lower = dff.copy()[col_name].str.lower()
				dff = dff.loc[df_lower.str.contains(filter_value)]
		
	return dff


def search_filter_lg(filter, df):
	dff = df
	filtering_expressions = filter.split(' && ')

	for filter_part in filtering_expressions:
		col_name, operator, filter_value = split_filter(filter_part)
		
		if (col_name == 'date') or (col_name == 'version_lvl2') or (col_name == 'version_lvl3'):
			filter_value = str(filter_value)

		# if there is search input
		if operator == 'contains':
			if isinstance(filter_value, float):
				dff = dff[dff[col_name]==int(filter_value)]
			else:
				df_lower = dff.copy()[col_name].str.lower()
				dff = dff.loc[df_lower.str.contains(filter_value)]
	
	return dff


def bar_rating(df):
	rating = df['rating'].value_counts()
	
	fig = px.bar(x=rating.index, y=rating,
				 title='Rating Distribution',
				 labels={'x':'Rating', 'y':'Number of Reviews'})
	return fig
	

def bar_sentiment(df):
	pos = df[df['sentiment']=='Positive']['day'].value_counts()
	neu = df[df['sentiment']=='Neutral']['day'].value_counts()
	neg = df[df['sentiment']=='Negative']['day'].value_counts()
	
	fig = go.Figure(data=[
		go.Bar(name='Positive', x=pos.index, y=pos, marker_color='#00CC96'),
		go.Bar(name='Neutral',  x=neu.index, y=neu, marker_color='#636EFA'),
		go.Bar(name='Negative', x=neg.index, y=neg, marker_color='#EF553B')
	])
	fig.update_layout(barmode='stack',
					  title_text='Sentiment Distribution by Day',
					  xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
							  'title':'Day'},
					  yaxis={'title':'Number of Reviews'})
					   
	return fig


def bar_version(df, col_name, title):
	dff = df.groupby(col_name)['rating'].mean()
	
	fig = px.bar(x=dff.index, y=dff, title=title,
				 labels={'x':'Version', 'y':'Average Rating'})
	
	return fig