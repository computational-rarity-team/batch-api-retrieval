    function callMB()
    {
        var req = new XMLHttpRequest()
        req.onreadystatechange = function()
        {
            if (req.readyState == 4)
            {
                if (req.status != 200)
                {
                    //error handling code here
                }
                else
                {
                    var response = JSON.parse(req.responseText)
                    if (response.title != null) {
                        document.getElementById('myDiv').innerHTML = response.title
                    } else {
                        if (response.name != null) {
                            document.getElementById('myDiv').innerHTML = response.name
                        } else {
                            if (response.description != null) {
                                document.getElementById('myDiv').innerHTML = response.description
                            } else {
                                document.getElementById('myDiv').innerHTML = "<p>Please enter something into the API tester.</p>"
                            }
                        }
                    }
                }
            }
        }
    
        req.open('POST', '/ajax')
        req.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
        var title = document.getElementById('title').value
        var name = document.getElementById('name').value
        var description = document.getElementById('description').value
        var postVars = 'title='+title+'&name='+name+'&description='+description
        req.send(postVars)
        
        return false
    }

    function callDC()
    {
        var req = new XMLHttpRequest()
        req.onreadystatechange = function()
        {
            if (req.readyState == 4)
            {
                if (req.status != 200)
                {
                    //error handling code here
                }
                else
                {
                    var response = JSON.parse(req.responseText)
                    console.log(response)
                    if (response.title != null || response.title != "") {
                        document.getElementById('myDiv').innerHTML = response.title
                    } else {
                        if (response.name != null) {
                            document.getElementById('myDiv').innerHTML = response.name
                        } else {
                            if (response.description != null) {
                                document.getElementById('myDiv').innerHTML = response.description
                            } else {
                                document.getElementById('myDiv').innerHTML = "<p>Please enter something into the API tester.</p>"
                            }
                        }
                    }
                }
            }
        }
    
        req.open('POST', '/ajax')
        req.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
        var title = document.getElementById('title').value
        var name = document.getElementById('name').value
        var description = document.getElementById('description').value
        var postVars = 'title='+title+'&name='+name+'&description='+description
        req.send(postVars)
        
        return false
    }

    function loadXMLDoc()
    {
        var req = new XMLHttpRequest()
        req.onreadystatechange = function()
        {
            if (req.readyState == 4)
            {
                if (req.status != 200)
                {
                    //error handling code here
                }
                else
                {
                    var response = JSON.parse(req.responseText)
                    document.getElementById('myDiv').innerHTML = response.title
                }
            }
        }
    
        req.open('POST', '/ajax')
        req.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
        var title = document.getElementById('title').value
        var name = document.getElementById('name').value
        var description = document.getElementById('description').value
        var postVars = 'title='+title+'&name='+name+'&description='+description
        req.send(postVars)
        
        return false
    }
