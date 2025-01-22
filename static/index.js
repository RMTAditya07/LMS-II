import router from "./router.js"
import Navbar from "./components/Navbar.js"

// const isAuthenticated = localStorage.getItem('auth-token') ? true : false

// router.beforeEach((to, from, next) => {
//     if(to.name !== 'Main' && !localStorage.getItem('auth-token') && !sessionStorage.getItem('user_id') ? true : false) 
//         next({name : 'Main'})
//     else next()
// })

new Vue({
    el:"#app",
    template: `<div>
    <Navbar :key='has_changed'/>
     <div class="col-md-10 content">
    <div class="container mt-4">
    <router-view />
    </div>
    </div>
    </div>
    
    `,
    router,
    components : {
        Navbar,
    },
    data:{
        has_changed: true,
    },
    watch: { 
        $route(to,from) {
            this.has_changed =!this.has_changed
        }
    }
})