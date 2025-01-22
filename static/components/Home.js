import AdminHome from "./AdminHome.js"
import StudentHome from "./StudentHome.js"

export default {
    
template:`<div>
<StudentHome v-if="userRole=='student'"/>
<AdminHome v-if="userRole=='admin'"/>
</div>`,

data(){
    return {
        userRole : localStorage.getItem('role'),
        authToken : localStorage.getItem('auth-token'),
        resources : [],
    }
},
components:{
    StudentHome,
    AdminHome,
},
async mounted(){
    console.log(this.userRole,this.authToken)
    const res = await fetch('/',{
        headers:{
            "Authentication-Token":this.authToken,
            'Content-Type': 'application/json',
        }
    })
    const data = await res.json()
    console.log(data)
    if (res.ok){
        this.resources = data
    }
    else{
        alert(data.message)
    }
}
}
