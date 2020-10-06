
import React from 'react';
import ReactDOM from 'react-dom';

import {
	ReactiveBase,
	DataSearch,
	DateRange,
	MultiList,
	SelectedFilters,
	DynamicRangeSlider,
	SingleDropdownList,
	ReactiveList
} from '@appbaseio/reactivesearch';

import {
	ReactiveGoogleMap,
	ReactiveOpenStreetMap
} from '@appbaseio/reactivemaps';

import {
	Row,
	Button,
	Col,
	Card,
	Collapse,
	Descriptions,
	Switch,
	Tree,
	Popover,
	Affix
} from 'antd';
import 'antd/dist/antd.css';
const { Panel } = Collapse;


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
	let { image_thumb, image_url, url, description, title } = {"description":"death_city","image":"","showRest":true,"title":"surname","url":""};
	// image = getNestedValue(res,image);
	image_thumb = "/registry/300/Volume 1_0235.jpg";
	image_url = "https://www.green-wood.com/scans/volume " +
		getNestedValue(res, "registry_volume").replace(/^0+/, '') +
		"/" + getNestedValue(res, "image_filename") +
		".jpg";
	title = getNestedValue(res,"name_full");
	url = getNestedValue(res,url);
	let death = getNestedValue(res,"death_date_iso");
	let aged = "(aged " + getNestedValue(res,"age_years") + " years)";
	let death_place = getNestedValue(res,"death_place_full");
	let death_cause = getNestedValue(res,"cause_of_death");
	let birth_place = getNestedValue(res,"birth_place_full");
	let tags =  getNestedValue(res, "tags").replace(/['"]+/g, '');
	// remove array's square brackets for display
	tags = tags.substring(1, tags.length-1);
	return (
		<Row onClick={triggerClickAnalytics} type="flex" gutter={16} key={res._id} style={{margin:'20px auto',borderBottom:'1px solid #ededed'}}>
			<Col span={image_url ? 6 : 0}>
				{image_url &&  <a href={image_url} target='registry_image'><img src={image_thumb} alt={title} width='200px;'/></a> }
			</Col>
			<Col span={image_url ? 18 : 24}>
				<Descriptions title={title} column={1} size="small" bordered>
					<Descriptions.Item label="Date of interment">{getNestedValue(res, "interment_date_display")}</Descriptions.Item>
					<Descriptions.Item label="Date of death">{getNestedValue(res, "death_date_display")}</Descriptions.Item>
					<Descriptions.Item label="Place of death">{death_place}</Descriptions.Item>
					<Descriptions.Item label="Cause of death">{death_cause}</Descriptions.Item>
					<Descriptions.Item label="Place of residence">{getNestedValue(res, "residence_place_full")}</Descriptions.Item>
					<Descriptions.Item label="Place of birth">{getNestedValue(res, "birth_place_full")}</Descriptions.Item>
					<Descriptions.Item label="Age">{getNestedValue(res,"age_full")}</Descriptions.Item>
					<Descriptions.Item label="Marital status">{getNestedValue(res,"marital_status")}</Descriptions.Item>
					<Descriptions.Item label="Cemetery">{getNestedValue(res,"cemetery")}</Descriptions.Item>
					<Descriptions.Item label="Grave location">{getNestedValue(res, "burial_location_current_grave")}</Descriptions.Item>
					<Descriptions.Item label="Grave lot number">{getNestedValue(res, "burial_location_current_lot")}</Descriptions.Item>
					<Descriptions.Item label="Interment ID">{getNestedValue(res, "interment_id")}</Descriptions.Item>
					<Descriptions.Item label="Undertaker">{getNestedValue(res, "undertaker")}</Descriptions.Item>
					<Descriptions.Item label="Tags">{tags}</Descriptions.Item>
				</Descriptions>

				{/*<Collapse ghost={true} defaultActiveKey={[]}>*/}
				{/*	<Panel header="Gravesite info" key="1">*/}
				{/*		<Descriptions column={1} size="small"  bordered>*/}
				{/*			<Descriptions.Item label="Cemetery">Green-Wood Cemetery, Brooklyn, NY, USA</Descriptions.Item>*/}
				{/*			<Descriptions.Item label="Date of burial">{getNestedValue(res, "cemetery_date")}</Descriptions.Item>*/}
				{/*			<Descriptions.Item label="Grave location">{getNestedValue(res, "grave_location")}</Descriptions.Item>*/}
				{/*			<Descriptions.Item label="Grave lot number">{getNestedValue(res, "lot_number")}</Descriptions.Item>*/}
				{/*			<Descriptions.Item label="Cemetery IDr">{getNestedValue(res, "id")}</Descriptions.Item>*/}
				{/*			<Descriptions.Item label="Undertaker">{getNestedValue(res, "undertaker")}</Descriptions.Item>*/}
				{/*		</Descriptions>*/}
				{/*	</Panel>*/}
				{/*</Collapse>*/}
			</Col>
			<div style={{padding:'20px'}}>
				{url ? <Button shape="circle" icon="link" style={{ marginRight: '5px' }} onClick={() => window.open(url, '_blank')} />
: null}
			</div>
		</Row>
	);
};

let onPopoverClickPlaceOfDeath = function(item) {
	if (typeof item !== 'undefined') {
		return <div>{item.death_geo_formatted_address}</div>;
	}
};
let onPopoverClickPlaceOfResidence = function(item) {
	if (typeof item !== 'undefined') {
		return <div>{item.residence_geo_formatted_address}</div>;
	}
};
let onPopoverClickPlaceOfBirth = function(item) {
	if (typeof item !== 'undefined') {
		return <div>{item.birth_geo_formatted_address}</div>;
	}
};

const CREDENTIALS = process.env.REACT_APP_ES_CREDENTIALS;
const ENDPOINT = process.env.REACT_APP_ES_ENDPOINT;
const INDEX = process.env.REACT_APP_ES_INDEX;
const App = () => (
	<ReactiveBase
		app={INDEX}
		url={ENDPOINT}
		credentials={CREDENTIALS}
	>
		<Row gutter={16} style={{ padding: 20 }}>
			<Col span={8}>
				<Collapse defaultActiveKey={['8', '9', '1', '2']}>
					{/*<Panel header="Cemetery" key="8">*/}
					{/*	<MultiList*/}
					{/*		componentId="cemetery_facet"*/}
					{/*		dataField="cemetery.keyword"*/}
					{/*		size={100}*/}
					{/*		style={{*/}
					{/*			marginBottom: 20*/}
					{/*		}}*/}
					{/*		filterLabel="Cemetery"*/}
					{/*		showSearch={false}*/}
					{/*		showCheckbox/>*/}
					{/*</Panel>*/}
					<Panel header="Registry" key="9">
						<DataSearch
							autosuggest={false}
							componentId="idSearch"
							filterLabel={"Interment ID"}
							componentType="DATASEARCH"
							dataField={['interment_id']}
							debounce={0}
							defaultValue={undefined}
							fieldWeights={[1]}
							fuzziness={0}
							highlight={false}
							placeholder="Search Interment IDs"
							queryFormat="and"
							showFilter={true}
							size={10}
							strictSelection={false}
							style={{
								marginBottom: 20
							}}
							URLParams={true}
							title="ID"
						/>
						<MultiList
							componentId="registry_volume_facet"
							dataField="registry_volume.keyword"
							size={100}
							style={{
								marginBottom: 20
							}}
							filterLabel="Registry volume"
							showSearch={false}
							showCheckbox
							URLParams={true}
							title="Volume"
						/>
						<MultiList
							componentId="registry_page_facet"
							dataField="registry_page.keyword"
							size={600}
							style={{
								marginBottom: 20
							}}
							sortBy="asc"
							filterLabel="Registry page"
							showSearch={false}
							showCount={false}
							URLParams={true}
							title="Page"
						/>
					</Panel>
					<Panel header="Cause of death" key="1">
						<MultiList
						  componentId="death_cause_facet"
						  dataField="cause_of_death.keyword"
						  size={100}
						  style={{
							marginBottom: 20
						  }}
						  filterLabel="Cause of death"
						 showCheckbox/>
					</Panel>
					<Panel header="Place of death" key="2" forceRender>
						<MultiList
							componentId="place_of_death_country_facet"
							dataField="death_country.keyword"
							showSearch={false}
							size={100}
							style={{
								marginBottom: 20
							}}
							title="Country"
							filterLabel="Place of death: country"
							showCheckbox/>
						<MultiList
							componentId="place_of_death_state_facet"
							dataField="death_state.keyword"
							showSearch={false}
							size={100}
							style={{
								marginBottom: 20
							}}
							title="State"
							filterLabel="Place of death: state"
							showCheckbox/>
						<MultiList
							componentId="place_of_death_city_facet"
							dataField="death_city.keyword"
							showSearch={false}
							size={100}
							style={{
								marginBottom: 20
							}}
							title="City"
							filterLabel="Place of death: city"
							showCheckbox/>
						{/*<MultiList*/}
						{/*	componentId="place_of_death_neighborhood_facet"*/}
						{/*	dataField="death_geo_neighborhood.keyword"*/}
						{/*	showSearch={false}*/}
						{/*	size={100}*/}
						{/*	style={{*/}
						{/*		marginBottom: 20*/}
						{/*	}}*/}
						{/*	title="Neighborhood"*/}
						{/*	filterLabel="Place of death: neighborhood"*/}
						{/*	showCheckbox/>*/}
						<MultiList
							componentId="place_of_death_hospital_facet"
							dataField="death_location.keyword"
							showSearch={false}
							size={100}
							style={{
								marginBottom: 20
							}}
							title="Location"
							filterLabel="Place of death: location"
							showCheckbox/>
						{/*<ReactiveOpenStreetMap*/}
						{/*	componentId="place_of_death"*/}
						{/*	dataField="death_geo_location"*/}
						{/*	title="Place of death"*/}
						{/*	size={1000}*/}
						{/*	autoCenter*/}
						{/*	style={{ height: '300px', width: '100%'}}*/}
						{/*	defaultZoom={2}*/}
						{/*	showSearchAsMove={false}*/}
						{/*	onPopoverClick={onPopoverClickPlaceOfDeath}*/}
						{/*	showMarkers={true}*/}
						{/*	// center={{ lat: 40.691265, lng: -73.9777743 }}*/}
						{/*/>*/}
						{/*<MultiList*/}
						{/*	componentId="place_of_death_facet"*/}
						{/*	dataField="place_of_death.keyword"*/}
						{/*	showSearch={false}*/}
						{/*	size={100}*/}
						{/*	style={{*/}
						{/*		marginBottom: 20*/}
						{/*	}}*/}
						{/*	title="Place of death"*/}
						{/*	filterLabel="Place of death"*/}
						{/*	showCheckbox/>*/}
						{/*<ReactiveGoogleMap*/}
						{/*	componentId="place_of_death"*/}
						{/*	dataField="death_location"*/}
						{/*	title="Place of death"*/}
						{/*	style={{ height: '300px', width: '100%'}}*/}
						{/*	zoom={25}*/}
						{/*	showSearchAsMove={false}*/}
						{/*	searchAsMove={false}*/}
						{/*/>*/}
					</Panel>
					<Panel header="Place of residence" key="3">
						<MultiList
							componentId="place_of_residence_country_facet"
							dataField="residence_country.keyword"
							showSearch={false}
							size={100}
							style={{
								marginBottom: 20
							}}
							title="Country"
							filterLabel="Place of residence: country"
							showCheckbox/>
						<MultiList
							componentId="residence_state_facet"
							dataField="residence_state.keyword"
							showSearch={false}
							size={100}
							style={{
								marginBottom: 20
							}}
							title="State"
							filterLabel="State"
							showCheckbox/>
						<MultiList
						  componentId="residence_city_facet"
						  dataField="residence_city.keyword"
						  showSearch={false}
						  size={100}
						  style={{
							marginBottom: 20
						  }}
						  title="City"
						  filterLabel="Residence: city"
						 showCheckbox/>
						{/*<MultiList*/}
						{/*	componentId="residence_neighborhood_facet"*/}
						{/*	dataField="residence_geo_neighborhood.keyword"*/}
						{/*	showSearch={false}*/}
						{/*	size={100}*/}
						{/*	style={{*/}
						{/*		marginBottom: 20*/}
						{/*	}}*/}
						{/*	title="Neighborhood"*/}
						{/*	filterLabel="Residence: neighborhood"*/}
						{/*	showCheckbox/>*/}
						{/*<ReactiveOpenStreetMap*/}
						{/*	componentId="place_of_residence_map"*/}
						{/*	dataField="residence_geo_location"*/}
						{/*	title="Place of residence"*/}
						{/*	size={1000}*/}
						{/*	autoCenter*/}
						{/*	style={{ height: '300px', width: '100%'}}*/}
						{/*	defaultZoom={2}*/}
						{/*	showSearchAsMove={false}*/}
						{/*	onPopoverClick={onPopoverClickPlaceOfResidence}*/}
						{/*	showMarkers={true}*/}
						{/*/>*/}
					</Panel>
					<Panel header="Place of birth" key="4">
						<MultiList
							componentId="place_of_birth_country_facet"
							dataField="birth_country.keyword"
							showSearch={false}
							size={100}
							style={{
								marginBottom: 20
							}}
							title="Country"
							filterLabel="Place of birth: country"
							showCheckbox/>
						<MultiList
							componentId="place_of_birth_state_facet"
							dataField="birth_state.keyword"
							showSearch={false}
							size={100}
							style={{
								marginBottom: 20
							}}
							title="State"
							filterLabel="Place of birth: state"
							showCheckbox/>
						<MultiList
							componentId="place_of_birth_city_facet"
							dataField="birth_city.keyword"
							showSearch={false}
							size={100}
							style={{
								marginBottom: 20
							}}
							title="City"
							filterLabel="Place of birth: city"
							showCheckbox/>
						{/*<ReactiveOpenStreetMap*/}
						{/*	componentId="place_of_birth_map"*/}
						{/*	dataField="birth_geo_location"*/}
						{/*	title="Place of birth"*/}
						{/*	size={1000}*/}
						{/*	autoCenter*/}
						{/*	style={{ height: '300px', width: '100%'}}*/}
						{/*	defaultZoom={2}*/}
						{/*	showSearchAsMove={false}*/}
						{/*	onPopoverClick={onPopoverClickPlaceOfBirth}*/}
						{/*	showMarkers={true}*/}
						{/*/>*/}
					</Panel>
					<Panel header="Marital status" key="5">
						<MultiList
							componentId="marital_status_facet"
							dataField="marital_status.keyword"
							showSearch={false}
							size={100}
							style={{
								marginBottom: 20
							}}
							filterLabel="Marital status"
							showCheckbox/>
					</Panel>
					<Panel header="Date of death" key="6">
						<DynamicRangeSlider
							componentId="death_year_facet"
							dataField="death_year"
							rangeLabels={(min, max) => ({
								start: min,
								end: max,
							})}
							stepValue={1}
							showHistogram={true}
							showFilter={true}
							interval={2}
							react={{
								and: ["CategoryFilter", "SearchFilter"]
							}}
							loader="Loading ..."
							filterLabel="Death year range"
							includeNullValues
						/>
					</Panel>
					<Panel header="Date of interment" key="6">
						<DynamicRangeSlider
							componentId="interment_year_facet"
							dataField="interment_year"
							rangeLabels={(min, max) => ({
								start: min,
								end: max,
							})}
							stepValue={1}
							showHistogram={true}
							showFilter={true}
							interval={2}
							react={{
								and: ["CategoryFilter", "SearchFilter"]
							}}
							loader="Loading ..."
							filterLabel="Interment year range"
							includeNullValues
							URLParams={true}
						/>
					</Panel>
						{/*<DateRange*/}
						{/*	componentId="death_date_facet"*/}
						{/*	title="Range"*/}
						{/*	dataField="death_date"*/}
						{/*	placeholder={{*/}
						{/*		start: 'Start Date',*/}
						{/*		end: 'End Date'*/}
						{/*	}}*/}
						{/*	focused={false}*/}
						{/*	numberOfMonths={1}*/}
						{/*	queryFormat="date"*/}
						{/*	autoFocusEnd={true}*/}
						{/*	showClear={true}*/}
						{/*	showFilter={true}*/}
						{/*	filterLabel="Death Date"*/}
						{/*	URLParams={false}*/}
						{/*	style={{*/}
						{/*		marginBottom: 20*/}
						{/*	}}*/}
						{/*/>*/}
					<Panel header="Age" key="7">
						<DynamicRangeSlider
							componentId="death_age_facet"
							dataField="age_years"
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
							loader="Loading ..."
							filterLabel="Age Range"
							includeNullValues
						/>
					</Panel>
				</Collapse>
			</Col>
			<Col span={16}>
				<DataSearch
					autosuggest={false}
					componentId="search"
					componentType="DATASEARCH"
					dataField={[
						'cause_of_death',
						'name_full',
						'name_last',
						'name_last.autosuggest',
						'name_last.english',
						'name_last.search',
						'name_first',
						'name_first.keyword',
						'residence_place_full',
						'tags'
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
					queryFormat="and"
					showFilter={true}
					size={20}
					strictSelection={false}
					style={{
						marginBottom: 20
					}}
					URLParams={true}
				/>

				<SelectedFilters />
				<div id="result">
					<ReactiveList
				  componentId="result"
				  dataField="_score"
				  pagination={true}
				  URLParams
				  react={{
				    and: [
				    	'death_cause_facet',
						'residence_city_facet',
						'death_date_facet',
						'death_year_facet',
						'interment_year_facet',
						'death_age_facet',
						'residence_state_facet',
						'place_of_death_facet',
						'marital_status_facet',
						'place_of_death_country_facet',
						'place_of_death_state_facet',
						'place_of_death_city_facet',
						'place_of_death_neighborhood_facet',
						'place_of_death_hospital_facet',
						'place_of_birth_country_facet',
						'place_of_birth_state_facet',
						'place_of_birth_city_facet',
						'place_of_residence_country_facet',
						'cemetery_facet',
						'search',
						'registry_volume_facet',
						'registry_page_facet',
						'idSearch'
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
