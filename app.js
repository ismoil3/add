const box=document.querySelector(".box")
const input=document.querySelector(".input")
const input1=document.querySelector(".input1")
const input2=document.querySelector(".input2")
const input3=document.querySelector(".input3")
const input4=document.querySelector(".input4")
const btnadd=document.querySelector(".btnadd")
let date=new Date()
let month=date.getMonth()
let day=date.getDate()
let year=date.getFullYear()
let ob=month+"/"+day+"/"+year
console.log(ob); 


let data=[
    {
        img:"https://www.rit.edu/cybersecurity/sites/rit.edu.cybersecurity/files/inline-images/phd-top-image.jpg",    
        id:"#1"
       ,name:"Ismoil Nasridinov",
         cre:"created on june 2024",
        p1:"Created on jule",
        h3:"Dreadline Date : 19/06/2024",
        h31:"Client Name : Munaroh Steffani",
        h32:"Location:India",
      
    }
]


let cnt=0
btnadd.onclick=()=>{
    const newObj={
    img: input1.value,
    id:data.length+1,
    name:input.value,
    cre:ob,
    p1:"Created on jule",
    h3:`Dreadline Date : ${input2.value}`,
    h31:`Client Name : ${input3.value}`,
    h32:`Location : ${input4.value}`,
    }
    cnt++
    if(input.value.trim()==""){
        return
      
    }
    if(input1.value.trim()==""){
        return alert("please ENTER url img")
      
    }
    if(input2.value.trim()==""){
        return alert("PLEASE ENTER DATE")
      
    }
    if(input3.value.trim()==""){
        return alert("PLEASE ENTER NEME CLIENT")
    }
    if(input4.value.trim()==""){
        return alert("PLEASE ENTER LOCATION")
      
    }
    else{
        data.push(newObj)
        getdate(data)
        input.value=""
        input1.value=""
        input2.value=""
        input3.value=""
        input4.value=""
    }
    
}

function Delet(id){
    data=data.filter((e)=>{
        return e.id !=id
    })
    getdate(data)
}
function getdate(data){
box.innerHTML=""
data.forEach((e,i) => {
    const card=document.createElement("div")
    const img=document.createElement("img")
    const id=document.createElement("p")
    const name=document.createElement("h3")
    const day=document.createElement("h3")
    const tr=document.createElement("p")
    const h3=document.createElement("h3")
    const cre=document.createElement("p")
    const h32=document.createElement("h3")
 
    const btndelet=document.createElement("button")
    btndelet.innerHTML="Delet"
    btndelet.onclick=()=>{
    Delet(e.id)
    }
    img.src=e.img
    img.style.width="300px"
     img.style.height="180px"
    card.style.width="300px"
    name.innerHTML=e.name
    id.innerHTML=`#${i+1}`
    cre.innerHTML=e.cre
    cre.classList.add("cre")
    day.innerHTML=e.h3
    h3.innerHTML=e.h31
    h32.innerHTML=e.h32
    img.classList.add("img")
    name.classList.add("name")
    card.append(img,id,name,cre,day,h3,h32,btndelet)
    box.appendChild(card)
    card.classList.add("card")
    name.classList.add("name")
    id.classList.add("id")
    h3.classList.add("h")
    tr.classList.add("tr")
    btndelet.classList.add("btndelet")
    

     name.classList.add("name")
     day.classList.add("day")
     cre.classList.add("p")
   

});
}
getdate(data)