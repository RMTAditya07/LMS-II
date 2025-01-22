import Home from "./components/Home.js"
import Login from "./components/Login.js"
import Users from "./components/Users.js"
import Sections from "./components/Sections.js"
import Books from "./components/Books.js"
import EditSection from "./components/EditSection.js"
import EditBook from "./components/EditBook.js"
import Section from "./components/Section.js"
import RequestDashboard from "./components/RequestDashboard.js"
import RequestBook from "./components/RequestBook.js"
import MyBooks from "./components/MyBooks.js"
import Chart from "./components/Chart.js"
import StudentStats from "./components/StudentStats.js"
import Downloads from "./components/Downloads.js"
import Main from "./components/Main.js"
// import StudyResourceForm from "./components/StudyResourceForm.js"

const routes = [
    {path:'/', component: Main, name:'Main'},
    {path:'/home', component: Home, name:'Home'},
    {path:'/login', component: Login, name:'Login'},
    {path :'/users', component: Users, name:'Users'},
    {path :'/sections', component: Sections, name:'Sections'},
    {path :'/books', component: Books, name:'Books'},
    { path: '/edit_section/:id', component: EditSection, name: 'EditSection', props: true },
    { path: '/edit_book/:id', component: EditBook, name: 'EditBook', props: true },
    { path: '/section/:id', component: Section, name: 'Section', props: true },
    { path: '/request-dashboard', component: RequestDashboard, name: 'RequestDashboard' },
    { path: '/my-requests', component: RequestBook, name: 'RequestBook'},
    { path: '/my-books', component: MyBooks, name: 'MyBooks'},
    { path: '/stats', component: Chart, name: 'Chart'},
    { path: '/my-stats', component: StudentStats, name: 'StudentStats' },
    { path: '/downloads', component: Downloads, name: 'Downloads' },
]

export default new VueRouter({
    routes, 
})