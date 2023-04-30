import { useState, useEffect } from 'react'
import axios from "axios";
import logo from './logo.svg';
import './App.css';
import DropDown from './DropDown';
import { ActionAreaCard } from './ActionAreaCard';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Button } from '@mui/material';

function TabPanel(props) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`simple-tabpanel-${index}`}
            aria-labelledby={`simple-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{ p: 3 }}>
                    <Typography>{children}</Typography>
                </Box>
            )}
        </div>
    );
}

function a11yProps(index) {
    return {
        id: `simple-tab-${index}`,
        'aria-controls': `simple-tabpanel-${index}`,
    };
}

function MainPage() {
    // new line start
    const [value, setValue] = useState(0);
    const [nprData, setNprData] = useState(null)
    const [mfData, setMfData] = useState(null)
    const [aecfData, setAecfData] = useState(null)

    const stateNames = { 'PA': 'Pennsylvania', 'FL': 'Florida', 'TN': 'Tennessee', 'IN': 'Indiana', 'MO': 'Missouri', 'LA': 'Louisiana', 'AZ': 'Arizona', 'NJ': 'New Jersey', 'NV': 'Nevada', 'AB': 'Alabama' }
    const users = ['0', '1', '2', '3']
    const typesDict = { 0: 'hotel', 1: 'restaurent', 2: 'nightlife' }
    const swappedStateNames = Object.entries(stateNames).reduce((acc, [key, value]) => {
        acc[value] = key;
        return acc;
    }, {});
    const handleChangeType = (event, newValue) => {
        setValue(newValue);
    };
    const stateValues = Object.values(stateNames);
    const [usState, setUsState] = useState(null)
    const [userId, setUserId] = useState(null)
    function getnprData(type, user, state) {
        axios({
            method: "GET",
            url: `/${type}/${state}/${user}/getNPR`,
        })
            .then((response) => {
                const res = response.data
                setNprData([...res]);
            }).catch((error) => {
                if (error.response) {
                    console.log(error.response)
                    console.log(error.response.status)
                    console.log(error.response.headers)
                }
            })
    }
    function getMfData(type, user, state) {
        axios({
            method: "GET",
            url: `/${type}/${state}/${user}/getMF`,
        })
            .then((response) => {
                const res = response.data
                setMfData([...res]);
            }).catch((error) => {
                if (error.response) {
                    console.log(error.response)
                    console.log(error.response.status)
                    console.log(error.response.headers)
                }
            })
    }
    function getAECFData(type, user, state) {
        axios({
            method: "GET",
            url: `/${type}/${state}/${user}/getAECF`,
        })
            .then((response) => {
                const res = response.data
                setAecfData([...res]);
            }).catch((error) => {
                if (error.response) {
                    console.log(error.response)
                    console.log(error.response.status)
                    console.log(error.response.headers)
                }
            })
    }

    useEffect(() => {
        if (usState && userId) {
            console.log(usState, userId)
            getnprData(typesDict[value], userId, swappedStateNames[usState])
            getMfData(typesDict[value], userId, swappedStateNames[usState])
            getAECFData(typesDict[value], userId, swappedStateNames[usState])
        }
    }, [usState, userId, value]);


    //end of new line 

    return (
        <div className="wrapper">
            <header>
                <div class="netflixLogo">
                    <a id="logo" href="#home"><img src="https://github.com/bassirishabh/Travelix/blob/master/public/travelix.png?raw=true" alt="Logo Image"></img></a>

                </div>
                <nav className="main-nav">
                    <Box sx={{ width: '100%', marginTop: "10px" }}>
                        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                            <Tabs value={value} onChange={handleChangeType} aria-label="basic tabs example">
                                <Tab sx={{ color: "white" }} label="Hotels" {...a11yProps(0)} />
                                <Tab sx={{ color: "white" }} label="Restaurants" {...a11yProps(1)} />
                                <Tab sx={{ color: "white" }} label="Night life" {...a11yProps(2)} />
                            </Tabs>
                        </Box>
                        <TabPanel value={value} index={0}>
                        </TabPanel>
                        <TabPanel value={value} index={1}>
                        </TabPanel>
                        <TabPanel value={value} index={2}>
                        </TabPanel>
                    </Box>
                    <Link to="/form">
                        <Button  variant="contained">New User</Button>
                    </Link>
                    <DropDown className="small-nav" options={users} state={userId} setState={setUserId} label="User" ></DropDown>
                    <DropDown className="small-nav" options={stateValues} state={usState} setState={setUsState} label="State"></DropDown>

                </nav>
                <nav className="sub-nav">
                    <a href="#"><i className="fas fa-search sub-nav-logo"></i></a>
                    <a href="#"><i className="fas fa-bell sub-nav-logo"></i></a>
                </nav>
            </header>

            <section className="main-container" >
                <div className="location" id="home">
                    <h1 id="home">Popular on Travelix</h1>
                    <div className="box">
                        {nprData && nprData.map(business => (
                            <ActionAreaCard business={business}></ActionAreaCard>
                        ))}
                    </div>
                </div>


                <h1 id="myList">Recommendations based on your Travel History</h1>
                <div className="box">
                    {mfData && mfData.map(business => (
                        <ActionAreaCard business={business}></ActionAreaCard>
                    ))}
                </div>

                <h1 id="tvShows">Recommendations based on your Preferences</h1>
                <div class="box">
                    {aecfData && aecfData.map(business => (
                        <ActionAreaCard business={business}></ActionAreaCard>
                    ))}
                </div>
            </section>
            <section className="link">
                <div className="logos">
                    <a href="#"><i className="fab fa-facebook-square fa-2x logo"></i></a>
                    <a href="#"><i className="fab fa-instagram fa-2x logo"></i></a>
                    <a href="#"><i className="fab fa-twitter fa-2x logo"></i></a>
                    <a href="#"><i className="fab fa-youtube fa-2x logo"></i></a>
                </div>
                <div className="sub-links">
                    <ul>
                        <li><a href="#">Hotels</a></li>
                        <li><a href="#">Restaurants</a></li>
                        <li><a href="#">Shopping</a></li>
                        <li><a href="#">Travel</a></li>
                        <li><a href="#">Tourism</a></li>
                        <li><a href="#">Business</a></li>
                        <li><a href="#">Users</a></li>
                        <li><a href="#">Terms of Use</a></li>
                        <li><a href="#">Privacy</a></li>
                        <li><a href="#">Legal Notices</a></li>
                        <li><a href="#">Corporate Information</a></li>
                        <li><a href="#">Contact Us</a></li>
                    </ul>
                </div>
            </section>

            <footer>
                <p>&copy; 2023 Travelix, Inc.</p>
                <p>&copy; RADS 2023</p>
            </footer>
        </div>
    );
}

export default MainPage;