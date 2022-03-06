import React from 'react';

import {
    DataSearch,
    DynamicRangeSlider,
    MultiList,
    ReactiveBase,
    ReactiveList,
    SelectedFilters
} from '@appbaseio/reactivesearch';

import {
    Col,
    Collapse,
    Descriptions,
    Row
} from 'antd';

import 'antd/dist/antd.css';

// import {
// 	ReactiveGoogleMap,
// 	ReactiveOpenStreetMap
// } from '@appbaseio/reactivemaps';
const { Panel } = Collapse;


function getNestedValue(obj, path) {
    const keys = path.split('.');
    const nestedValue = keys.reduce((value, key) => {
        if (value) {
            return value[key];
        }
        return '';
    }, obj);
    if (typeof nestedValue === 'object') {
        return JSON.stringify(nestedValue);
    }
    return nestedValue;
}

function renderItem(res, triggerClickAnalytics) {
    let image_thumb = "/registry/300/Volume 1_0235.jpg";
    let image_url = "https://www.green-wood.com/scans/Volume " +
        getNestedValue(res, "registry_volume") +
        "/" + getNestedValue(res, "registry_image") +
        ".jpg";

    // let birth_place_url = '';
    // let birth_place_id = getNestedValue(res, 'birth_geo_place_id');
    // if (birth_place_id !== '') {
    //     birth_place_url =
    //         "https://www.google.com/maps/search/?api=1&query=" +
    //         getNestedValue(res, 'birth_geo_formatted_address') + "&query_place_id=" +
    //         getNestedValue(res, 'birth_geo_place_id');
    // }

    // let residence_place_url = '';
    // let residence_place_id = getNestedValue(res, 'residence_geo_place_id');
    // if (residence_place_id !== '') {
    //     residence_place_url =
    //         "https://www.google.com/maps/search/?api=1&query=" +
    //         getNestedValue(res, 'residence_geo_formatted_address') + "&query_place_id=" +
    //         getNestedValue(res, 'residence_place_geo_place_id');
    // }

    // let tags =  getNestedValue(res, "tags").replace(/['"]+/g, '');
    // remove array's square brackets for display
    // tags = tags.substring(1, tags.length-1);
    return (
        <Row onClick={triggerClickAnalytics} type="flex" gutter={16} key={res._id} style={{margin:'20px auto',borderBottom:'1px solid #ededed'}}>
            <Col span={image_url ? 6 : 0}>
                {image_url &&  <a href={image_url} target='registry_image'><img src={image_thumb} alt={getNestedValue(res,"name_display")} width='200px;'/></a> }
            </Col>
            <Col span={image_url ? 18 : 24}>
                <Descriptions title={getNestedValue(res,"name_display")} column={1} size="small" bordered>
                    <Descriptions.Item label="Date of interment">{getNestedValue(res, "interment_date_display")}</Descriptions.Item>
                    <Descriptions.Item label="Date of death">{getNestedValue(res, "death_date_display")}</Descriptions.Item>
                    <Descriptions.Item label="Place of death">{getNestedValue(res,"death_place_display")}</Descriptions.Item>
                    <Descriptions.Item label="Cause of death">{getNestedValue(res,"cause_of_death_display")}</Descriptions.Item>
                    <Descriptions.Item label="Place of residence">{getNestedValue(res, "residence_place_street_display") }, &nbsp;
                        {getNestedValue(res, "residence_place_city_display") }</Descriptions.Item>
                    <Descriptions.Item label="Place of birth">{getNestedValue(res, "birth_place_displayed")}</Descriptions.Item>
                    <Descriptions.Item label="Age">{getNestedValue(res,"age_display")}</Descriptions.Item>
                    <Descriptions.Item label="Marital status">{getNestedValue(res,"marital_status")}</Descriptions.Item>
                    <Descriptions.Item label="Gender (guess)">{getNestedValue(res,"gender_guess")}</Descriptions.Item>
                    {/*<Descriptions.Item label="Cemetery">{getNestedValue(res,"cemetery")}</Descriptions.Item>*/}
                    <Descriptions.Item label="Grave location">{getNestedValue(res, "burial_location_grave_current")}</Descriptions.Item>
                    <Descriptions.Item label="Grave lot number">{getNestedValue(res, "burial_location_lot_current")}</Descriptions.Item>
                    <Descriptions.Item label="Is lot owner?">{getNestedValue(res, "is_lot_owner")}</Descriptions.Item>
                    <Descriptions.Item label="Registry volume">{getNestedValue(res, "registry_volume")}</Descriptions.Item>
                    <Descriptions.Item label="Registry page">{getNestedValue(res, "registry_page")}</Descriptions.Item>
                    <Descriptions.Item label="Interment ID">{getNestedValue(res, "interment_id")}</Descriptions.Item>
                    <Descriptions.Item label="Undertaker">{getNestedValue(res, "undertaker_display")}</Descriptions.Item>
                    {/*<Descriptions.Item label="Tags">{tags}</Descriptions.Item>*/}
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
        </Row>
    );
}

// let onPopoverClickPlaceOfDeath = function(item) {
// 	if (typeof item !== 'undefined') {
// 		return <div>{item.death_geo_formatted_address}</div>;
// 	}
// };
// let onPopoverClickPlaceOfResidence = function(item) {
// 	if (typeof item !== 'undefined') {
// 		return <div>{item.residence_geo_formatted_address}</div>;
// 	}
// };
// let onPopoverClickPlaceOfBirth = function(item) {
// 	if (typeof item !== 'undefined') {
// 		return <div>{item.birth_geo_formatted_address}</div>;
// 	}
// };

const CREDENTIALS = process.env.REACT_APP_ES_CREDENTIALS;
const ENDPOINT = process.env.REACT_APP_ES_ENDPOINT;
const INDEX = process.env.REACT_APP_ES_INDEX;
const App = () => (
    <ReactiveBase
        app={INDEX}
        url={ENDPOINT}
        credentials={CREDENTIALS}>

        <Row gutter={16} style={{ padding: 20 }}>
            <Col span={8}>
                <Collapse defaultActiveKey={['10', '1', '6']}>
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
                    <Panel header="Registry" key="10">
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
                            sortBy="asc"
                            title="Volume"
                        />
                        {/*<MultiList*/}
                        {/*    componentId="registry_page_facet"*/}
                        {/*    dataField="registry_page.keyword"*/}
                        {/*    size={600}*/}
                        {/*    style={{*/}
                        {/*        marginBottom: 20*/}
                        {/*    }}*/}
                        {/*    sortBy="asc"*/}
                        {/*    filterLabel="Registry page"*/}
                        {/*    showSearch={false}*/}
                        {/*    showCount={false}*/}
                        {/*    URLParams={true}*/}
                        {/*    title="Page"*/}
                        {/*/>*/}
                    </Panel>
                    <Panel header="Cause of death" key="1">
                        <MultiList
                            componentId="death_cause_facet"
                            dataField="cause_of_death_display.keyword"
                            size={100}
                            style={{
                                marginBottom: 20
                            }}
                            filterLabel="Cause of death"
                            URLParams={true}
                            showCheckbox/>
                    </Panel>

                    <Panel header="Undertaker" key="11">
                        <MultiList
                            componentId="undertaker_facet"
                            dataField="undertaker_display.keyword"
                            size={100}
                            style={{
                                marginBottom: 20
                            }}
                            filterLabel="Undertaker"
                            URLParams={true}
                            showCheckbox/>
                    </Panel>

                    <Panel header="Place of death" key="2">
                        <MultiList
                            componentId="death_place_display_facet"
                            dataField="death_place_display.keyword"
                            size={100}
                            style={{
                                marginBottom: 20
                            }}
                            title="Place of death"
                            filterLabel="Place of death"
                            URLParams={true}
                            showCheckbox/>
                    </Panel>

                    <Panel header="Place of residence" key="3">
                         <MultiList
                            componentId="residence_place_city_display_facet"
                            dataField="residence_place_city_display.keyword"
                            size={100}
                            style={{
                                marginBottom: 20
                            }}
                            title="Place of residence"
                            filterLabel="Place of residence"
                            URLParams={true}
                            showCheckbox/>
                    </Panel>

                    <Panel header="Place of birth" key="4">
                         <MultiList
                            componentId="birth_place_displayed_facet"
                            dataField="birth_place_displayed.keyword"
                            size={100}
                            style={{
                                marginBottom: 20
                            }}
                            title="Place of birth"
                            filterLabel="Place of birth"
                            URLParams={true}
                            showCheckbox/>
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
                            URLParams={true}
                            showCheckbox/>
                    </Panel>
                    <Panel header="Gender (guess based on first name)" key="6">
                        <MultiList
                            componentId="gender_guess_facet"
                            dataField="gender_guess.keyword"
                            showSearch={false}
                            size={100}
                            style={{
                                marginBottom: 20
                            }}
                            filterLabel="Gender guess"
                            URLParams={true}
                            showCheckbox/>
                    </Panel>
                    <Panel header="Date of death" key="7">
                        <DynamicRangeSlider
                            componentId="death_year_facet"
                            dataField="death_date_year_transcribed"
                            rangeLabels={(min, max) => ({
                                start: min,
                                end: max,
                            })}
                            stepValue={1}
                            tooltipTrigger={"always"}
                            showHistogram={true}
                            showFilter={true}
                            interval={2}
                            react={{
                                and: ["CategoryFilter", "SearchFilter"]
                            }}
                            loader="Loading ..."
                            filterLabel="Death year range"
                            URLParams={true}
                        />
                    </Panel>
                    <Panel header="Date of interment" key="8">
                        <DynamicRangeSlider
                            componentId="interment_year_facet"
                            dataField="interment_date_year_transcribed"
                            rangeLabels={(min, max) => ({
                                start: min,
                                end: max,
                            })}
                            stepValue={1}
                            tooltipTrigger={"always"}
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
                    <Panel header="Age" key="9">
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
                            tooltipTrigger={"always"}
                            showHistogram={true}
                            showFilter={true}
                            interval={2}
                            react={{
                                and: ["CategoryFilter", "SearchFilter"]
                            }}
                            loader="Loading ..."
                            filterLabel="Age Range"
                            URLParams={true}
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
                        'undertaker_display',
                        'cause_of_death_display',
                        'name_display',
                        'name_last',
                        'name_last.autosuggest',
                        'name_last.english',
                        'name_last.search',
                        'name_first',
                        'name_first.keyword',
                        'birth_place_displayed',
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
                        'forename'
                    ]}
                    placeholder="Search"
                    queryFormat="and"
                    searchOperators={true}
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
                                'undertaker_facet',
                                'death_cause_facet',
                                'death_date_facet',
                                'death_year_facet',
                                'interment_year_facet',
                                'death_age_facet',
                                'marital_status_facet',
                                'cemetery_facet',
                                'search',
                                'registry_volume_facet',
                                'registry_page_facet',
                                'idSearch',
                                'gender_guess_facet',
                                'death_place_display_facet',
                                'residence_place_city_display_facet',
                                'birth_place_displayed_facet'
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

export default App;