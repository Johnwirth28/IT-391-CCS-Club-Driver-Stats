let cars = []


function showAddCar() {
    const form = document.getElementById('add-car')
    form.style.display = form.style.display === 'block' ? 'none' : 'block';
    if(form.style.display === 'block'){
        document.getElementById('car-make').focus();
    }
    
}

function addCar(){
    const carMake = document.getElementById('car-make').value.trim();
    const carModel = document.getElementById('car-model').value.trim();
    const carYear = document.getElementById('car-year').value.trim();
    const carColor = document.getElementById('car-color').value.trim();
    const carFrontPSI = document.getElementById('car-front-psi').value.trim();
    const carBackPSI = document.getElementById('car-back-psi').value.trim();


    if(carMake === '' || carModel === ''){
        alert("Car make or model cannot be empty");
        return;
    }
    const car = {
        make: carMake,
        model: carModel,
        year: carYear,
        color: carColor,
        frontPSI: carFrontPSI,
        backPSI: carBackPSI
    }


    cars.push(car);

    document.getElementById('car-make').value = '';
    document.getElementById('car-model').value = '';
    document.getElementById('car-year').value = '';
    document.getElementById('car-color').value = '';
    document.getElementById('car-front-psi').value = '';
    document.getElementById('car-back-psi').value = '';

    renderCars();
    document.getElementById('add-car').style.display = 'none';
}

function removeAllCars(){
    if (cars.length == 0 ){
        alert("No cars to remove");
        return;
    }
    if(confirm("Are you sure you want to remove all cars?")){
        cars = [];
        renderCars();
    }

}

function deleteCar(index){
    if(confirmDeleteCar()){
        cars.splice(index, 1);
        renderCars();
    }
}

function confirmDeleteCar()
{

    return confirm("Are you sure you want to delete this car?");
}

function renderCars(){
    const carList = document.getElementById('car-list');

    if(cars.length == 0)
    {
        carList.innerHTML = '<li>No cars in the garage. Please add a car.</li>';
        return;
    }

    carList.innerHTML = '';

    cars.forEach((car, index) => {
        const li = document.createElement('li');
        li.className = 'car-item';

        const span = document.createElement('span');

        let carText = `${car.year} ${car.make} ${car.model}`;
        if(car.color) carText += ` - ${car.color}`;
        if(car.frontPSI || car.backPSI)
        {
            carText += ', Front Tire PSI: ' + (car.frontPSI ? car.frontPSI : 'N/A') + ', Back Tire PSI: ' + (car.backPSI ? car.backPSI : 'N/A');
        }
        
        span.textContent = carText;

        const deleteButton = document.createElement('button');
        deleteButton.className = 'remove-btn';
        deleteButton.textContent = 'Delete';
        deleteButton.onclick = () => deleteCar(index);

        li.appendChild(span);
        li.appendChild(deleteButton);
        carList.appendChild(li);
    });
}

renderCars();