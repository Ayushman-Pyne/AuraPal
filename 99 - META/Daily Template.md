---
date: <%tp.date.now("YYYY-MM-DD")%>T<%tp.date.now("HH:mm")%>
tags:
  - Daily
cssclasses:
  - daily<%tp.date.now("dddd",0,tp.file.title,"YYYYMMDD").toLowerCase()%>
---

## <% tp.date.now("dddd, MMMM Do, YYYY", 0, tp.file.title, "YYYYMMDD") %>
***
### Schedule for the Day
<%* if (tp.date.now("ddd", 0, tp.file.title, "YYYYMMDD") === "Mon") {
-%> 
- [ ] Analog and Digital Electronics
- [ ] Data Structures and Algorithms LAB
- [ ] Data Structures and Algorithms LAB
- [ ] Computer Organization LAB
<%* } 
else if (tp.date.now("ddd", 0, tp.file.title, "YYYYMMDD") === "Tue") {
-%>
- [ ] Economics For Engineers (Humanities II)
- [ ] Analog and Digital Electronics
- [ ] IT Workshop (Scilab/ MathLAB/ Python/ R)
- [ ] Computer Organization 
<%* }
else if (tp.date.now("ddd", 0, tp.file.title, "YYYYMMDD") === "Wed") {
-%>
- [ ] Analog and Digital Electronics
- [ ] Analog and Digital Electronics LAB
- [ ] Analog and Digital Electronics LAB
- [ ] Mathematics III
<%* } 
else if (tp.date.now("ddd", 0, tp.file.title, "YYYYMMDD") === "Thu") {
-%>
- [ ] Economics For Engineers (Humanities II)
- [ ] Computer Organization 
- [ ] Data Structures and Algorithms
- [ ] Mathematics III
<%* }
else if (tp.date.now("ddd", 0, tp.file.title, "YYYYMMDD") === "Fri") {
-%>
- [ ] Economics For Engineers (Humanities II)
- [ ] Mathematics III
- [ ] Computer Organization 
- [ ] Mathematics III
<%* }
else if (tp.date.now("ddd", 0, tp.file.title, "YYYYMMDD") === "Sat") {
-%>
- [ ] Data Structures and Algorithms 
- [ ] Data Structures and Algorithms 
- [ ] Computer Organization LAB
- [ ] IT Workshop (Scilab/ MathLAB/ Python/ R)
<%* } -%>

***
### All Notes

<%* if (tp.date.now("ddd", 0, tp.file.title, "YYYYMMDD") === "Mon") {
-%> 
#### Analog and Digital Electronics



#### Data Structures and Algorithms LAB



#### Data Structures and Algorithms LAB



#### Computer Organization LAB



<%* } 
else if (tp.date.now("ddd", 0, tp.file.title, "YYYYMMDD") === "Tue") {
-%>
#### Economics For Engineers (Humanities II)



#### Analog and Digital Electronics



#### IT Workshop (Scilab/ MathLAB/ Python/ R)



#### Computer Organization 



<%* }
else if (tp.date.now("ddd", 0, tp.file.title, "YYYYMMDD") === "Wed") {
-%>
#### Analog and Digital Electronics



#### Analog and Digital Electronics LAB



#### Analog and Digital Electronics LAB



#### Mathematics III



<%* } 
else if (tp.date.now("ddd", 0, tp.file.title, "YYYYMMDD") === "Thu") {
-%>
#### Economics For Engineers (Humanities II)



#### Computer Organization 



#### Data Structures and Algorithms 



#### Mathematics III



<%* }
else if (tp.date.now("ddd", 0, tp.file.title, "YYYYMMDD") === "Fri") {
-%>
#### Economics For Engineers (Humanities II)



#### Mathematics III



#### Computer Organization 



#### Mathematics III



<%* }
else if (tp.date.now("ddd", 0, tp.file.title, "YYYYMMDD") === "Sat") {
-%>
#### Data Structures and Algorithms 



#### Data Structures and Algorithms 



#### Computer Organization LAB



#### IT Workshop (Scilab/ MathLAB/ Python/ R)



<%* } -%>



***
### Tasks
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3