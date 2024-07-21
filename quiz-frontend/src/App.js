import React, { useState } from 'react';
import {
  ChakraProvider,
  Box,
  VStack,
  Heading,
  Text,
  Input,
  Button,
  Radio,
  RadioGroup,
  Stack,
  Alert,
  AlertIcon,
  Container,
  Divider,
} from '@chakra-ui/react';

function App() {
  const [topic, setTopic] = useState('');
  const [summary, setSummary] = useState('');
  const [quiz, setQuiz] = useState(null);
  const [error, setError] = useState(null);
  const [showQuiz, setShowQuiz] = useState(false);
  const [userAnswers, setUserAnswers] = useState({});
  const [revealAnswers, setRevealAnswers] = useState(false);

  const handleTopicChange = (event) => setTopic(event.target.value);

  const handleTopicSubmit = () => {
    setError(null);
    setSummary('');
    setQuiz(null);
    setShowQuiz(false);
    setUserAnswers({});
    setRevealAnswers(false);

    fetch('http://localhost:8090/submit_topic/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
        } else {
          setSummary(data.summary);
          setQuiz(data.quiz);
        }
      })
      .catch((error) => {
        console.error('Error:', error);
        setError('An error occurred while fetching data');
      });
  };

  const handleGenerateQuiz = () => setShowQuiz(true);

  const handleAnswerSelect = (questionIndex, selectedAnswer) => {
    setUserAnswers({ ...userAnswers, [questionIndex]: selectedAnswer });
  };

  const handleSubmitQuiz = () => setRevealAnswers(true);

  const handleRestart = () => {
    setTopic('');
    setSummary('');
    setQuiz(null);
    setError(null);
    setShowQuiz(false);
    setUserAnswers({});
    setRevealAnswers(false);
  };

  return (
    <ChakraProvider>
      <Box minHeight="100vh" bg="gray.900" py={10}>
        <Container maxW="container.md">
          <VStack spacing={8} align="stretch">
            <Heading as="h1" size="2xl" textAlign="center" color="blue.300">
              Quiz App
            </Heading>
            
            <Box>
              <Input
                value={topic}
                onChange={handleTopicChange}
                placeholder="Enter topic"
                size="lg"
                mb={4}
                bg="gray.700"
                borderColor="gray.600"
                _hover={{ borderColor: "gray.500" }}
                _focus={{ borderColor: "blue.300", boxShadow: "0 0 0 1px #63B3ED" }}
                 color="white"
              />
              <Button onClick={handleTopicSubmit} colorScheme="blue" size="lg" width="full">
                Submit Topic
              </Button>
            </Box>

            {error && (
              <Alert status="error" borderRadius="md">
                <AlertIcon />
                {error}
              </Alert>
            )}

            {summary && (
              <Box bg="gray.800" p={6} borderRadius="md" boxShadow="md">
                <Heading as="h2" size="lg" color="blue.300" mb={4}>Summary</Heading>
                <Text color="white">{summary}</Text>
                {!showQuiz && (
                  <Button onClick={handleGenerateQuiz} colorScheme="green" mt={6} width="full">
                    Generate Quiz
                  </Button>
                )}
              </Box>
            )}

            {showQuiz && quiz && (
              <Box bg="gray.800" p={6} borderRadius="md" boxShadow="md">
                <Heading as="h2" size="lg" color="blue.300" mb={6}>Quiz</Heading>
                {quiz.map((question, index) => (
                  <Box key={index} mb={8}>
                    <Text fontWeight="bold" fontSize="lg" mb={3} color="white">
                      Q{index + 1}: {question.question}
                    </Text>
                    <RadioGroup
                      onChange={(value) => handleAnswerSelect(index, value)}
                      value={userAnswers[index]}
                    >
                      <Stack>
                        {question.options.map((option, optionIndex) => (
                          <Radio
                            key={optionIndex}
                            value={option}
                            colorScheme="blue"
                          >
                            <Text color="white">{option}</Text>
                            {revealAnswers && option === question.answer && (
                              <Text as="span" color="green.400" ml={2} fontWeight="bold">✓</Text>
                            )}
                          </Radio>
                        ))}
                      </Stack>
                    </RadioGroup>
                    {revealAnswers && (
                      <Text
                        color={userAnswers[index] === question.answer ? "green.400" : "red.400"}
                        mt={2}
                        fontWeight="bold"
                      >
                        Your answer: {userAnswers[index] || 'Not answered'}
                      </Text>
                    )}
                  </Box>
                ))}
                {!revealAnswers && (
                  <Button onClick={handleSubmitQuiz} colorScheme="purple" width="full">
                    Submit Quiz
                  </Button>
                )}
              </Box>
            )}

            <Divider borderColor="gray.600" />

            <Button onClick={handleRestart} colorScheme="teal" size="lg">
              Restart with New Topic
            </Button>
          </VStack>
        </Container>
      </Box>
    </ChakraProvider>
  );
}

export default App;