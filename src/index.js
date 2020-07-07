

import React from 'react';
import ReactDOM from 'react-dom';

import {
	ReactiveBase,
	DataSearch,
	MultiList,
	SelectedFilters,
	ReactiveList
} from '@appbaseio/reactivesearch';
import {
	Row,
	Button,
	Col,
	Card,
	Switch,
	Tree,
	Popover,
	Affix
} from 'antd';
import 'antd/dist/antd.css';


function getNestedValue(obj, path) {
	const keys = path.split('.');
	const currentObject = obj;
	const nestedValue = keys.reduce((value, key) => {
		if (value) {
		return value[key];
		}
		return '';
	}, currentObject);
	if (typeof nestedValue === 'object') {
		return JSON.stringify(nestedValue);
	}
	return nestedValue;
}

function renderItem(res, triggerClickAnalytics) {
	let { image, url, description, title } = {"description":"death_city","image":"","showRest":true,"title":"surname","url":""};
	image = getNestedValue(res,image);
	title = getNestedValue(res,title);
	url = getNestedValue(res,url);
	description = getNestedValue(res,description)
	return (
		<Row onClick={triggerClickAnalytics} type="flex" gutter={16} key={res._id} style={{margin:'20px auto',borderBottom:'1px solid #ededed'}}>
			<Col span={image ? 6 : 0}>
				{image &&  <img src={image} alt={title} /> }
			</Col>
			<Col span={image ? 18 : 24}>
				<h3 style={{ fontWeight: '600' }} dangerouslySetInnerHTML={{__html: title || 'Choose a valid Title Field'}}/>
				<p style={{ fontSize: '1em' }} dangerouslySetInnerHTML={{__html: description || 'Choose a valid Description Field'}}/>
			</Col>
			<div style={{padding:'20px'}}>
				{url ? <Button shape="circle" icon="link" style={{ marginRight: '5px' }} onClick={() => window.open(url, '_blank')} />
: null}
			</div>
		</Row>
	);
};

const API_KEY = process.env.REACT_APP_API_KEY;
const App = () => (
	<ReactiveBase
		app="greenwood"
		credentials={API_KEY}
		url="https://scalr.api.appbase.io"
		analytics={true}
		searchStateHeader
	>
		<Row gutter={16} style={{ padding: 20 }}>
			<Col span={12}>
				<Card>
				<MultiList
				  componentId="list-3"
				  dataField="death_cause.keyword"
				  size={100}
				  style={{
				    marginBottom: 20
				  }}
				  title="Cause of death"
				/>
				<MultiList
				  componentId="list-4"
				  dataField="late_residence_city.keyword"
				  showSearch={false}
				  size={100}
				  style={{
				    marginBottom: 20
				  }}
				  title="City"
				/>
				</Card>
			</Col>
			<Col span={12}>
				<DataSearch
				  componentId="search"
				  dataField={[
				    'age',
				    'age.keyword',
				    'surname',
				    'surname.autosuggest',
				    'surname.english',
				    'surname.search'
				  ]}
				  fieldWeights={[
				    1,
				    1,
				    1,
				    1,
				    1,
				    1
				  ]}
				  fuzziness={0}
				  highlight={true}
				  highlightField={[
				    'age',
				    'surname'
				  ]}
				  style={{
				    marginBottom: 20
				  }}
				/>

				<SelectedFilters />
				<div id="result">
					<ReactiveList
				  componentId="result"
				  dataField="_score"
				  pagination={true}
				  react={{
				    and: [
				      'list-3',
				      'search',
				      'list-4'
				    ]
				  }}
				  renderItem={renderItem}
				  size={5}
				  style={{
				    marginTop: 20
				  }}
				/>
				</div>
			</Col>
			
		</Row>
	</ReactiveBase>
);

ReactDOM.render(
	<App />,
	document.getElementById('root')
);
