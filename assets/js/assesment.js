const quizContainer = document.getElementById("quiz");
const resultsContainer = document.getElementById("results");
const submitButton = document.getElementById("submit");

function showResults() {
     // Debugging: Log to check if quizContainer is defined
     console.log("quizContainer:", quizContainer);

     // gather answer containers from our quiz
     const answerContainers = quizContainer ? quizContainer.querySelectorAll(".answers") : [];
     
     // Debugging: Log to check if answerContainers is defined
    //  console.log("answerContainers:", answerContainers);
 
     answerContainers.forEach(e => e.style.color = "black");

    // keep track of user's answers
    let numCorrect = 0;

    // for each question...
    myQuestions.forEach((currentQuestion, questionNumber) => {
        // find selected answer
        const answerContainer = answerContainers[questionNumber];
        // console.log("Ques Num:",questionNumber);
        // console.log("Ans Container:",answerContainer);
        const selector = `input[name=question${questionNumber}]:checked`;
        const userAnswer = (answerContainer.querySelector(selector) || {}).value;
        for(i in userAnswer) console.log("user Ans:",i);
        // console.log("corr Ans:",currentQuestion.correctAnswer);
        // if answer is correct
        if (userAnswer === currentQuestion.correctAnswer) {
            // add to the number of correct answers
            numCorrect++;

            // color the answers green
            answerContainers[questionNumber].style.color = "green";
        } else {
            // if answer is wrong or blank
            // color the answers red
            answerContainers[questionNumber].style.color = "red";
        }
    });

    // show number of correct answers out of total
    resultsContainer.innerHTML = `${numCorrect} out of ${myQuestions.length}`;
}



submitButton.addEventListener("click", showResults);
