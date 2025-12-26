document.addEventListener("DOMContentLoaded", () => {
            const links = [
                /*
                {text: "Event Schedule", href : "schedule_race.html"},
                {text: "Stats", href : "stats.html"},
                {text: "Login", href : "login.html"},
                */
                { text: "Event Schedule", href: "/schedule_race" },
                { text: "Stats", href: "/stats" },
                { text: "Login", href: "/login" },
            ];

            const taskbar = document.createElement("div");
            taskbar.className = "taskbar";

            links.forEach(link=>{
                const a = document.createElement("a");
                a.textContent =link.text;
                a.href = link.href;
                

                if(link.text === "Login"){
                    a.className = "right";
                }

                taskbar.appendChild(a);
            });

            document.getElementById("taskbar-container").appendChild(taskbar);
        });
            
