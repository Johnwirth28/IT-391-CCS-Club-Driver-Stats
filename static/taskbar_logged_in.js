
document.addEventListener("DOMContentLoaded", () => {
    const links = [
        /*
        {text: "Home", href : "driver_status_logged_in_home.html"},
        {text: "Event Schedule", href : "schedule_race_logged_in.html"},
        {text: "Stats", href : "logged_in_stats.html"},
        {text: "Personal Stats", href : "personal_stats.html"},
        {text: "Weather", href : "weather.html"},
        */
        {text: "Home", href : "/home_logged_in"},
        {text: "Event Schedule", href : "/schedule_race_logged_in"},
        {text: "Stats", href : "/stats_logged_in"}, 
        {text: "Personal Stats", href : "/personal_stats"},
        {text: "Weather", href : "/weather"},
    ];

    const taskbar = document.createElement("div");
    taskbar.className = "taskbar";

    // Create hamburger button so small screens can toggle the menu
    const hamburger = document.createElement("button");
    hamburger.className = "hamburger";
    hamburger.setAttribute('aria-label', 'Toggle menu');
    hamburger.innerHTML = '<span class="bar"></span><span class="bar"></span><span class="bar"></span>';
    hamburger.addEventListener('click', () => {
        taskbar.classList.toggle('active');
    });

    taskbar.appendChild(hamburger);

    links.forEach(link=>{
        const a = document.createElement("a");
        a.textContent =link.text;
        a.href = link.href;

        if(link.text === "Profile"){
            a.className = "right";
        }

        taskbar.appendChild(a);
    });

    const profileDropDown = document.createElement("div");
    profileDropDown.className = "dropdown right";

    const profileButton = document.createElement("button");
    profileButton.className = "dropbtn";
    profileButton.textContent = "Profile";

    const dropdownContent = document.createElement("div");
    dropdownContent.className = "dropdown-content";
    
    const profileLink = document.createElement("a");
    profileLink.textContent = "View Profile";
    //profileLink.href = "profile.html";//change this
    profileLink.href = "/profile"

    const garageLink = document.createElement("a");
    garageLink.textContent = "Garage";
    //garageLink.href = "garage.html";//change this
     garageLink.href = "/garage"

    const signOutLink = document.createElement("a");
    signOutLink.textContent = "Sign Out";
   // signOutLink.href = "driver_status_home.html"
    signOutLink.href = "/logout";
    dropdownContent.appendChild(profileLink);
    dropdownContent.appendChild(garageLink);
    dropdownContent.appendChild(signOutLink);

    profileDropDown.appendChild(profileButton);
    profileDropDown.appendChild(dropdownContent);
    taskbar.appendChild(profileDropDown);



        document.getElementById("taskbar-container").appendChild(taskbar);
});


        