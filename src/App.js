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
    Row,
    // Drawer,
    // Button,
    Tooltip,
} from 'antd';

import {
  ReadFilled,
} from '@ant-design/icons';

import 'antd/dist/antd.css';

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
    // let image_thumb = "./registry/thumbnail.jpg";
    let image_url = "https://www.green-wood.com/scans/Volume " +
        getNestedValue(res, "registry_volume") +
        "/" + getNestedValue(res, "registry_image") +
        ".jpg";
    // let id_search_url = "/?idSearch=%22" + getNestedValue(res, "interment_id") + "%22";
    // let  image_url = null;
    // let registry_page_url = "https://www.green-wood.com/scans/Volume " +
    //     getNestedValue(res, "registry_volume") +
    //     "/" + getNestedValue(res, "registry_image") +
    //     ".jpg";

    let residence_place_composed = '';
    let residence_street = getNestedValue(res, "residence_place_street_display");
    let residence_city = getNestedValue(res, "residence_place_city_display");
    if (residence_street !== '') {
        residence_place_composed += residence_street;
        if (residence_city !== '') {
            residence_place_composed += ', ' + residence_city;
        }
    } else {
        residence_place_composed = residence_city;
    }

    // let tags =  getNestedValue(res, "tags").replace(/['"]+/g, '');
    // remove array's square brackets for display
    // tags = tags.substring(1, tags.length-1);
    return (
        <Row key={res._id} style={{margin:'20px auto',borderBottom:'1px solid #ededed'}}>
            <Col span={24}>
                <Descriptions
                    // title={getNestedValue(res,"name_display")}
                    column={{
                        xxl: 1,
                        xl: 1,
                        lg: 1,
                        md: 1,
                        sm: 1,
                        xs: 1,
                      }}
                    labelStyle={{width: "25%"}}
                    bordered>
                    <Descriptions.Item label="Name">
                        <Tooltip title="Click to view the scanned registry page in a new tab.">
                            <a href={image_url} target="registry_image">
                                <b>{getNestedValue(res, "name_display")}</b>
                                &nbsp;&nbsp;
                                <ReadFilled/>
                            </a>
                        </Tooltip>

                    </Descriptions.Item>
                    { getNestedValue(res, "interment_date_display").length > 0 && (
                        <Descriptions.Item label="Date of interment">{getNestedValue(res, "interment_date_display")}</Descriptions.Item>
                    )}
                    { getNestedValue(res, "burial_location_lot_current").length > 0 && (
                        <Descriptions.Item label="Lot number (of current burial site)">{getNestedValue(res, "burial_location_lot_current")}</Descriptions.Item>
                    )}
                    { getNestedValue(res, "burial_location_grave_current").length > 0 && (
                        <Descriptions.Item label="Grave number (of current burial site)">{getNestedValue(res, "burial_location_grave_current")}</Descriptions.Item>
                    )}
                </Descriptions>

                <Collapse ghost={true} defaultActiveKey={[]}>
                	<Panel header="show more" key="1">
                		<Descriptions
                            column={{
                                xxl: 1,
                                xl: 1,
                                lg: 1,
                                md: 1,
                                sm: 1,
                                xs: 1,
                              }}
                            labelStyle={{width: "25%"}}
                            bordered>
                            { getNestedValue(res, "birth_place_displayed").length > 0 && (
                                <Descriptions.Item label="Birthplace">{getNestedValue(res, "birth_place_displayed")}</Descriptions.Item>
                            )}
                            { getNestedValue(res, "marital_status").length > 0 && (
                                <Descriptions.Item label="Marital status">{getNestedValue(res,"marital_status")}</Descriptions.Item>
                            )}
                            { getNestedValue(res, "age_display").length > 0 && (
                                <Descriptions.Item label="Age at death">{getNestedValue(res,"age_display")}</Descriptions.Item>
                            )}
                            { residence_place_composed.length > 0 && (
                                <Descriptions.Item label="Late residence">{residence_place_composed}</Descriptions.Item>
                            )}
                            { getNestedValue(res, "death_place_display").length > 0 && (
                                <Descriptions.Item label="Place of death">{getNestedValue(res,"death_place_display")}</Descriptions.Item>
                            )}
                            { getNestedValue(res, "cause_of_death_display").length > 0 && (
                                <Descriptions.Item label="Cause of death">{getNestedValue(res,"cause_of_death_display")}</Descriptions.Item>
                            )}
                            { getNestedValue(res, "death_date_display").length > 0 && (
                                <Descriptions.Item label="Date of death">{getNestedValue(res, "death_date_display")}</Descriptions.Item>
                            )}
                            { getNestedValue(res, "burial_location_lot_previous").length > 0 && (
                                <Descriptions.Item label="Lot number (of previous burial site)">{getNestedValue(res, "burial_location_lot_previous")}</Descriptions.Item>
                            )}
                            { getNestedValue(res, "burial_location_grave_previous").length > 0 && (
                                <Descriptions.Item label="Grave number (of previous burial site)">{getNestedValue(res, "burial_location_grave_previous")}</Descriptions.Item>
                            )}
                            { getNestedValue(res, "has_diagram") !== null && (
                            <Descriptions.Item label="Diagram available (see digital image)">{getNestedValue(res, "has_diagram").toString()}</Descriptions.Item>
                            )}
                            { getNestedValue(res, "is_lot_owner") !== null && (
                                <Descriptions.Item
                                    label="Lot owner?">{getNestedValue(res, "is_lot_owner").toString()}</Descriptions.Item>
                            )}
                            { getNestedValue(res, "undertaker_display").length > 0 && (
                                <Descriptions.Item label="Undertaker / Funeral Director">{getNestedValue(res, "undertaker_display")}</Descriptions.Item>
                            )}
                            { getNestedValue(res, "remarks_display").length > 0 && (
                                <Descriptions.Item label="Notes & Remarks">{getNestedValue(res, "remarks_display")}</Descriptions.Item>
                            )}
                            { getNestedValue(res, "registry_volume").length > 0 && (
                                <Descriptions.Item label="Burial Registry Volume">{getNestedValue(res, "registry_volume")}</Descriptions.Item>
                            )}
                            { getNestedValue(res, "registry_image").length > 0 && (
                                <Descriptions.Item label="Burial Registry Page">
                                    <Tooltip title="Click to view the scanned registry page in a new tab.">
                                        <a href={image_url} target="registry_page">
                                            {getNestedValue(res, "registry_page")}
                                            &nbsp;&nbsp;
                                            <ReadFilled/>
                                        </a>
                                    </Tooltip>
                                </Descriptions.Item>
                            )}
                            {/*{ getNestedValue(res, "interment_id").length > 0 && (*/}
                                <Descriptions.Item label="Interment Number">
                                    {/*<a href={id_search_url} target="interment_id">*/}
                                        {getNestedValue(res, "interment_id")}
                                    {/*</a>*/}
                                </Descriptions.Item>
                		    {/*)}*/}
                            </Descriptions>
                	</Panel>
                </Collapse>

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


const App = () => {

    // const [visible, setVisible] = useState(false);
    //
    // const showDrawer = () => {
    //   setVisible(true);
    // };
    //
    // const onClose = () => {
    //     setVisible(false);
    // };

    return (
            <ReactiveBase
                app={INDEX}
                url={ENDPOINT}
                credentials={CREDENTIALS}
                style={{padding: 20}}
                // enableAppbase={true}
            >

            {/*<Drawer*/}
            {/*    id="filters"*/}
            {/*    title="Search Filters"*/}
            {/*    onClose={onClose}*/}
            {/*    placement="left"*/}
            {/*    width={378}*/}
            {/*    visible={visible}*/}
            {/*>*/}

            <Row gutter={16} style={{ padding: 20 }}>
            <Col>

                <Collapse defaultActiveKey={['33']}>

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

                    <Panel header="Name" key="33">
                        <DataSearch
                            autosuggest={false}
                            componentId="name_facet"
                            filterLabel={"Name"}
                            componentType="DATASEARCH"
                            dataField={[
                                'name_display',
                                'name_transcribed',
                                'name_last',
                                'name_first',
                                'name_middle',
                            ]}
                            debounce={0}
                            defaultValue={undefined}
                            fieldWeights={[1]}
                            fuzziness={0}
                            highlight={false}
                            placeholder="Search by name"
                            queryFormat="or"
                            showFilter={true}
                            size={10}
                            strictSelection={false}
                            style={{
                                marginBottom: 20
                            }}
                            URLParams={true}
                            title="Name"
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

                    <Panel header="Birthplace" key="4">
                         <MultiList
                            componentId="birth_place_displayed_facet"
                            dataField="birth_place_displayed.keyword"
                            size={500}
                            style={{
                                marginBottom: 20
                            }}
                            title="Birthplace"
                            filterLabel="Birthplace"
                            sortBy="asc"
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

                     <Panel header="Age at death" key="9">
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

                    <Panel header="Late residence" key="3">
                         <MultiList
                            componentId="residence_place_city_display_facet"
                            dataField="residence_place_city_display.keyword"
                            size={500}
                            style={{
                                marginBottom: 20
                            }}
                            title="Late residence"
                            filterLabel="Late residence"
                            sortBy="asc"
                            URLParams={true}
                            showCheckbox/>
                    </Panel>

                    <Panel header="Place of death" key="2">
                        <MultiList
                            componentId="death_place_display_facet"
                            dataField="death_place_display.keyword"
                            size={500}
                            style={{
                                marginBottom: 20
                            }}
                            title="Place of death"
                            filterLabel="Place of death"
                            URLParams={true}
                            sortBy="asc"
                            showCheckbox/>
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

                    <Panel header="Undertaker / Funeral Director" key="11">
                        <MultiList
                            componentId="undertaker_facet"
                            dataField="undertaker_display.keyword"
                            size={100}
                            style={{
                                marginBottom: 20
                            }}
                            filterLabel="Undertaker / Funeral Director"
                            URLParams={true}
                            showCheckbox/>
                    </Panel>

                    {/*<Panel header="Gender (guess based on first name)" key="6">*/}
                    {/*    <MultiList*/}
                    {/*        componentId="gender_guess_facet"*/}
                    {/*        dataField="gender_guess.keyword"*/}
                    {/*        showSearch={false}*/}
                    {/*        size={100}*/}
                    {/*        style={{*/}
                    {/*            marginBottom: 20*/}
                    {/*        }}*/}
                    {/*        filterLabel="Gender guess"*/}
                    {/*        URLParams={true}*/}
                    {/*        showCheckbox/>*/}
                    {/*</Panel>*/}

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

                    <Panel header="Burial registry" key="10">
                        <DataSearch
                            autosuggest={false}
                            componentId="idSearch"
                            filterLabel={"Interment Number"}
                            componentType="DATASEARCH"
                            dataField={['interment_id']}
                            debounce={0}
                            defaultValue={undefined}
                            fieldWeights={[1]}
                            fuzziness={0}
                            highlight={false}
                            placeholder="Search interment numbers"
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
                            filterLabel="Burial registry volume"
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
                </Collapse>
            </Col>

            {/*</Drawer>*/}
            <Col span={16}>
                       <DataSearch
                            autosuggest={false}
                            componentId="search"
                            dataField={[
                                "name_last",
                                "name_first",
                                "name_transcribed",
                                "name_display",
                                "name_middle",
                                "burial_location_lot_current",
                                "burial_location_lot_previous",
                                "burial_location_grave_current",
                                "burial_location_grave_previous",
                                "birth_place_displayed",
                                "birth_place_transcribed",
                                "residence_place_city_display",
                                "residence_place_city_transcribed",
                                "residence_place_street_display",
                                "residence_place_street_transcribed",
                                "death_place_display",
                                "death_place_transcribed",
                                "death_date_display",
                                "death_date_iso",
                                "interment_date_display",
                                "interment_date_iso",
                                "cause_of_death_display",
                                "undertaker_transcribed",
                                "undertaker_display",
                                "remarks_display",
                                "marital_status",
                            ]}
                            fieldWeights={[
                                3,
                                3,
                                3,
                                3,
                                3,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1,
                                1
                            ]}
                            debounce={100}
                            defaultValue={undefined}
                            fuzziness={0}
                            highlight={false}
                            highlightField={[
                            ]}
                            placeholder="Search"
                            queryFormat="or"
                            queryString={true}
                            searchOperators={true}
                            showFilter={true}
                            strictSelection={false}
                            style={{
                                marginTop: 20,
                                marginBottom: 10,
                                marginRight: 12,
                                display: 'inline-block',
                                width: '75%'
                            }}
                            URLParams={false}
                        />
                        {/*<Button*/}
                        {/*    type="primary"*/}
                        {/*    onClick={showDrawer}*/}
                        {/*    style={{*/}
                        {/*        marginBottom: 10*/}
                        {/*    }}*/}
                        {/*>*/}
                        {/*    Filters*/}
                        {/*</Button>*/}

                        <SelectedFilters/>
                        <div id="result">
                            <ReactiveList
                                componentId="result"
                                dataField="_score"
                                pagination={true}
                                paginationAt="bottom"
                                pages={10}
                                URLParams
                                excludeFields={[
                                    "birth_place_geo_location",
                                    "death_place_geo_place_id",
                                    "death_place_geo_country_long",
                                    "residence_place_geo_state_short",
                                    "death_place_geo_is_faulty",
                                    "residence_place_geo_county",
                                    "residence_place_geo_state_long",
                                    "birth_geo_state_long",
                                    "residence_place_geo_neighborhood",
                                    "residence_place_geo_country_short",
                                    "residence_place_geo_place_id",
                                    "residence_place_geo_is_faulty",
                                    "death_place_geo_street_number_long",
                                    "death_place_geo_zip",
                                    "birth_geo_place_id",
                                    "residence_place_geo_street_number_short",
                                    "birth_geo_zip",
                                    "birth_geo_street_name_short",
                                    "residence_place_geo_formatted_address",
                                    "residence_place_geo_street_number_long",
                                    "birth_geo_county",
                                    "death_place_geo_formatted_address",
                                    "residence_place_geo_city",
                                    "residence_place_geo_location",
                                    "residence_place_geo_street_number",
                                    "birth_geo_city",
                                    "birth_geo_formatted_address",
                                    "residence_place_geo_country_long",
                                    "death_place_geo_country_short",
                                    "death_place_geo_county",
                                    "death_date_ult_month",
                                    "death_place_geo_location",
                                    "birth_geo_country_short",
                                    "death_place_geo_neighborhood",
                                    "birth_geo_street_number",
                                    "birth_geo_state_short",
                                    "birth_geo_country_long",
                                    "birth_geo_is_faulty",
                                    "birth_geo_street_name_long",
                                    "death_place_geo_state_short",
                                    "death_place_geo_city",
                                    "residence_place_geo_zip",
                                    "death_place_geo_street_number_short",
                                    "death_place_geo_street_number",
                                    "birth_geo_neighborhood",
                                    "death_place_geo_state_long",


                                ]}
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
                                        'birth_place_displayed_facet',
                                        'name_facet',
                                    ]
                                }}
                                renderItem={renderItem}
                                showResultStats={true}
                                // renderResultStats={function(stats) {
                                //     return `Showing ${stats.displayedResults} of total ${stats.numberOfResults} in ${
                                //         stats.time
                                //     } ms`;
                                // }}
                                size={10}
                                defaultQuery={() => ({ track_total_hits: true })}
                                style={{
                                    marginTop: 20
                                }}
                                sortOptions={[
                                    {
                                      dataField: "interment_date_year_transcribed",
                                      sortBy: "desc",
                                      label: "Sort by interment year (High to Low) \u00A0",
                                    },
                                    {
                                      dataField: "interment_date_year_transcribed",
                                      sortBy: "asc",
                                      label: "Sort by interment year (Low to High) \u00A0",
                                    },
                                    {
                                      dataField: "name_last.keyword",
                                      sortBy: "asc",
                                      label: "Sort by last name (A-Z) \u00A0",
                                    },
                                    {
                                      dataField: "name_last.keyword",
                                      sortBy: "desc",
                                      label: "Sort by last name (Z-A) \u00A0",
                                    },
                                    {
                                      dataField: "age_years",
                                      sortBy: "desc",
                                      label: "Sort by age (High to Low) \u00A0",
                                    },
                                    {
                                      dataField: "age_years",
                                      sortBy: "asc",
                                      label: "Sort by age (Low to High) \u00A0",
                                    },
                                    {
                                      dataField: "interment_id.keyword",
                                      sortBy: "desc",
                                      label: "Sort by interment number (High to Low) \u00A0",
                                    },
                                    {
                                      dataField: "interment_id.keyword",
                                      sortBy: "asc",
                                      label: "Sort by interment number (Low to High) \u00A0",
                                    },

                                ]}
                            />
                        </div>
            </Col>
            </Row>

            </ReactiveBase>
    );
};

export default App;