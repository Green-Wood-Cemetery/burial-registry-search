

import React from 'react';
import ReactDOM from 'react-dom';

import {
	ReactiveBase,
	DataSearch,
	DateRange,
	MultiList,
	SelectedFilters,
	DynamicRangeSlider,
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
	title = getNestedValue(res,"surname") + ", " + getNestedValue(res,"forename");
	url = getNestedValue(res,url);
	let death = getNestedValue(res,"death_date") + " (aged " + getNestedValue(res,"age") + " years)";
	let death_place = getNestedValue(res,"place_of_death");
	let death_cause = "Cause: " + getNestedValue(res,"death_cause");
	let birth_place = getNestedValue(res,"birth_place");
	return (
		<Row onClick={triggerClickAnalytics} type="flex" gutter={16} key={res._id} style={{margin:'20px auto',borderBottom:'1px solid #ededed'}}>
			<Col span={image ? 6 : 0}>
				{image &&  <img src={image} alt={title} /> }
			</Col>
			<Col span={image ? 18 : 24}>
				<h3 style={{ fontWeight: '600' }} dangerouslySetInnerHTML={{__html: title || 'Choose a valid Title Field'}}/>
				<h4 style={{ fontWeight: '600' }}>Died</h4>
				<p style={{ fontSize: '1em' }} dangerouslySetInnerHTML={{__html: death || 'Choose a valid field'}}/>
				<p style={{ fontSize: '1em' }} dangerouslySetInnerHTML={{__html: death_place || 'Choose a valid field'}}/>
				<p style={{ fontSize: '1em' }} dangerouslySetInnerHTML={{__html: death_cause || 'Choose a valid field'}}/>
				<h4 style={{ fontWeight: '600' }}>Born</h4>
				<p style={{ fontSize: '1em' }} dangerouslySetInnerHTML={{__html: birth_place || 'Choose a valid field'}}/>
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
				  componentId="death_cause_facet"
				  dataField="death_cause.keyword"
				  size={100}
				  style={{
				    marginBottom: 20
				  }}
				  title="Cause of death"
				 showCheckbox/>
				<MultiList
				  componentId="residence_city_facet"
				  dataField="late_residence_city.keyword"
				  showSearch={false}
				  size={100}
				  style={{
				    marginBottom: 20
				  }}
				  title="City"
				 showCheckbox/>
				<DateRange
					componentId="death_date_facet"
					dataField="death_date"
					title="Death Date"
					defaultValue={{
						start: new Date('1840-01-01'),
						end: new Date('2020-01-01')
					}}
					placeholder={{
						start: 'Start Date',
						end: 'End Date'
					}}
					focused={false}
					numberOfMonths={1}
					queryFormat="date"
					autoFocusEnd={true}
					showClear={true}
					showFilter={true}
					filterLabel="Death Date"
					URLParams={false}
				/>
				<DynamicRangeSlider
					componentId="death_age_facet"
					dataField="age"
					title="Age Range"
					defaultValue={(min, max) => (
						{
							"start": 0,
							"end": 110
						}
					)}
					rangeLabels={(min, max) => (
						{
							"start": "0 years",
							"end": "110 years"
						}
					)}
					stepValue={1}
					showHistogram={true}
					showFilter={true}
					interval={2}
					react={{
						and: ["CategoryFilter", "SearchFilter"]
					}}
					URLParams={true}
					loader="Loading ..."
					filterLabel="Age Range"
				/>
				</Card>
			</Col>
			<Col span={12}>
				<DataSearch
					autosuggest={true}
					componentId="search"
					componentType="DATASEARCH"
					dataField={[
						'surname',
						'surname.autosuggest',
						'surname.english',
						'surname.search',
						'late_residence_city',
						'late_residence_city.keyword',
						'forename',
						'forename.keyword'
					]}
					debounce={0}
					defaultValue={undefined}
					fieldWeights={[
						1,
						1,
						1,
						1,
						1,
						1,
						1,
						1
					]}
					fuzziness={0}
					highlight={false}
					highlightField={[
						'surname',
						'late_residence_city',
						'forename'
					]}
					placeholder="Search"
					queryFormat="or"
					showFilter={true}
					size={20}
					strictSelection={false}
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
				    	'death_cause_facet',
						'residence_city_facet',
						'death_date_facet',
						'death_age_facet'
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
