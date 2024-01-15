<h1 align='center'> Credentials </h1>
<hr>



<h3><b>Admin credentials:</b><br></h3> 
<b>username:</b> admin <br>
<b>pw:</b> fuseadmin<br>
<hr>

<h3><b>User credentials:</b><br></h3>
<b>username:</b> user<br>
<b>pw:</b> fuseuser

<hr>
<h3> Building Docker Container </h3>
sudo docker build -t classify_annotation_tool .

<h3> Running Docker Container </h3>
sudo docker run -d -p 8501:8501 classify_annotation_tool
