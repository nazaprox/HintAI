```tsx
/**
 * HintAI
 * frontend/App.tsx
 *
 * Point d'entrée principal Expo / React Native.
 *
 * Fichiers frontend autorisés :
 *   frontend/App.tsx
 *   frontend/components.tsx
 *   frontend/styles.ts
 *
 * AUCUN autre fichier frontend n'est nécessaire.
 */

import React, {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  ActivityIndicator,
  Animated,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StatusBar,
  Text,
  TextInput,
  View,
} from "react-native";

import {
  Camera,
  FileText,
  Image as ImageIcon,
  Lightbulb,
  BookOpen,
  History,
  User,
  Sparkles,
  Send,
  ChevronRight,
  CheckCircle,
  AlertCircle,
  Upload,
  Crown,
  Zap,
} from "lucide-react-native";

import {
  styles,
  COLORS,
} from "./styles";

import {
  AppButton,
  Card,
  EmptyState,
  LoadingView,
  SourceSelector,
  BottomNavigation,
  ExerciseCard,
  PlanCard,
  MessageBubble,
  QualityBadge,
} from "./components";


/* ============================================================
   TYPES
   ============================================================ */

type Screen =
  | "help"
  | "learn"
  | "history"
  | "profile";

type InputMode =
  | "text"
  | "camera"
  | "image"
  | "pdf";

type UserPlan =
  | "free"
  | "basic"
  | "pro"
  | "proplus"
  | "super"
  | "heavy";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

type HistoryItem = {
  id: string;
  type: "help" | "learn";
  title: string;
  date: string;
};

type User = {
  id?: string;
  name?: string;
  email?: string;
  plan?: UserPlan;
};

type Credits = {
  balance: number;
  monthly?: number;
  used?: number;
};


/* ============================================================
   CONFIGURATION
   ============================================================ */

const API_URL =
  process.env.EXPO_PUBLIC_API_URL ||
  "https://YOUR-VERCEL-BACKEND.vercel.app";

const APP_NAME = "HintAI";


const PLANS = [
  {
    id: "free" as UserPlan,
    name: "Free",
    price: "0 €",
    description: "Pour commencer",
  },
  {
    id: "basic" as UserPlan,
    name: "Basic",
    price: "5 €",
    description: "Pour progresser régulièrement",
  },
  {
    id: "pro" as UserPlan,
    name: "Pro",
    price: "10 €",
    description: "Pour un apprentissage intensif",
  },
  {
    id: "proplus" as UserPlan,
    name: "Pro+",
    price: "15 €",
    description: "Plus de crédits et de possibilités",
  },
  {
    id: "super" as UserPlan,
    name: "Super",
    price: "20 €",
    description: "Pour les gros besoins",
  },
  {
    id: "heavy" as UserPlan,
    name: "Heavy",
    price: "30 €",
    description: "Pour une utilisation maximale",
  },
];


/* ============================================================
   APP
   ============================================================ */

export default function App() {

  const [screen, setScreen] =
    useState<Screen>("help");

  const [user, setUser] =
    useState<User | null>(null);

  const [credits, setCredits] =
    useState<Credits>({
      balance: 0,
    });

  const [history, setHistory] =
    useState<HistoryItem[]>([]);

  const [booting, setBooting] =
    useState(true);


  /*
   * Animation globale.
   */

  const fade =
    useRef(
      new Animated.Value(0)
    ).current;

  const translateY =
    useRef(
      new Animated.Value(18)
    ).current;


  useEffect(() => {

    Animated.parallel([
      Animated.timing(
        fade,
        {
          toValue: 1,
          duration: 550,
          useNativeDriver: true,
        }
      ),

      Animated.spring(
        translateY,
        {
          toValue: 0,
          friction: 8,
          tension: 50,
          useNativeDriver: true,
        }
      ),
    ]).start();

  }, [fade, translateY]);


  /*
   * Initialisation locale.
   *
   * L'historique est volontairement conservé côté appareil.
   */

  useEffect(() => {

    initialize();

  }, []);


  async function initialize() {

    try {

      const storedHistory =
        await loadLocalHistory();

      setHistory(
        storedHistory
      );


      /*
       * La session sera reliée au backend.
       * Si aucune session n'existe, HintAI fonctionne
       * quand même en mode local jusqu'à l'authentification.
       */

      const session =
        await getSession();

      if (session) {

        setUser(
          session.user
        );

        setCredits(
          session.credits || {
            balance: 0,
          }
        );
      }

    } catch (error) {

      console.log(
        "HintAI initialization error:",
        error
      );

    } finally {

      setBooting(false);
    }
  }


  if (booting) {

    return (
      <SafeAreaView
        style={
          styles.loadingScreen
        }
      >

        <StatusBar
          barStyle="light-content"
        />

        <Animated.View
          style={[
            styles.loadingContent,
            {
              opacity: fade,
              transform: [
                {
                  translateY,
                },
              ],
            },
          ]}
        >

          <View
            style={
              styles.loadingLogo
            }
          >

            <Sparkles
              size={34}
              color={
                COLORS.primary
              }
            />

          </View>

          <Text
            style={
              styles.loadingTitle
            }
          >
            HintAI
          </Text>

          <Text
            style={
              styles.loadingSubtitle
            }
          >
            Apprendre. Comprendre. Réussir.
          </Text>

          <ActivityIndicator
            size="large"
            color={
              COLORS.primary
            }
            style={
              styles.loadingSpinner
            }
          />

        </Animated.View>

      </SafeAreaView>
    );
  }


  return (
    <SafeAreaView
      style={
        styles.app
      }
    >

      <StatusBar
        barStyle="light-content"
        backgroundColor={
          COLORS.background
        }
      />

      <Header
        user={user}
        credits={credits}
        onProfile={() =>
          setScreen("profile")
        }
      />


      <Animated.View
        style={[
          styles.main,
          {
            opacity: fade,
            transform: [
              {
                translateY,
              },
            ],
          },
        ]}
      >

        {screen === "help" && (

          <HelpMeScreen
            credits={credits}
            onCreditsChange={
              setCredits
            }
            onHistoryChange={
              setHistory
            }
          />

        )}


        {screen === "learn" && (

          <LearnScreen
            credits={credits}
            onCreditsChange={
              setCredits
            }
          />

        )}


        {screen === "history" && (

          <HistoryScreen
            history={
              history
            }
          />

        )}


        {screen === "profile" && (

          <ProfileScreen
            user={user}
            credits={credits}
            onUserChange={
              setUser
            }
          />

        )}

      </Animated.View>


      <BottomNavigation
        activeScreen={
          screen
        }
        onChange={
          setScreen
        }
      />

    </SafeAreaView>
  );
}


/* ============================================================
   HEADER
   ============================================================ */

function Header({
  user,
  credits,
  onProfile,
}: {
  user: User | null;
  credits: Credits;
  onProfile: () => void;
}) {

  return (
    <View
      style={
        styles.header
      }
    >

      <View
        style={
          styles.brandContainer
        }
      >

        <View
          style={
            styles.brandIcon
          }
        >

          <Sparkles
            size={20}
            color={
              COLORS.primary
            }
          />

        </View>

        <View>

          <Text
            style={
              styles.brandTitle
            }
          >
            HintAI
          </Text>

          <Text
            style={
              styles.brandSubtitle
            }
          >
            Learn smarter
          </Text>

        </View>

      </View>


      <View
        style={
          styles.headerRight
        }
      >

        <View
          style={
            styles.creditBadge
          }
        >

          <Zap
            size={15}
            color={
              COLORS.warning
            }
          />

          <Text
            style={
              styles.creditValue
            }
          >
            {credits.balance}
          </Text>

        </View>


        <Pressable
          onPress={
            onProfile
          }
          style={
            styles.avatar
          }
        >

          <Text
            style={
              styles.avatarText
            }
          >
            {
              (
                user?.name ||
                user?.email ||
                "H"
              )
                .charAt(0)
                .toUpperCase()
            }
          </Text>

        </Pressable>

      </View>

    </View>
  );
}


/* ============================================================
   HELP ME
   ============================================================ */

function HelpMeScreen({
  credits,
  onCreditsChange,
  onHistoryChange,
}: {
  credits: Credits;
  onCreditsChange: (
    credits: Credits
  ) => void;
  onHistoryChange: (
    history: HistoryItem[]
  ) => void;
}) {

  const [inputMode, setInputMode] =
    useState<InputMode>("text");

  const [exerciseText, setExerciseText] =
    useState("");

  const [selectedFile, setSelectedFile] =
    useState<any>(null);

  const [loading, setLoading] =
    useState(false);

  const [directSolution, setDirectSolution] =
    useState(false);

  const [conversationId, setConversationId] =
    useState<string | null>(null);

  const [hintLevel, setHintLevel] =
    useState(0);

  const [answer, setAnswer] =
    useState("");

  const [messages, setMessages] =
    useState<Message[]>([]);

  const [streaming, setStreaming] =
    useState(false);

  const [quality, setQuality] =
    useState<any>(null);


  /*
   * Sélection d'une image/PDF/caméra.
   *
   * Le contrôle OpenCV.js reste local au frontend.
   * Le backend reçoit uniquement le résultat validé.
   */

  async function selectInput(
    mode: InputMode
  ) {

    setInputMode(
      mode
    );

    setSelectedFile(
      null
    );

    if (mode === "text") {
      return;
    }

    try {

      const file =
        await pickInput(
          mode
        );

      if (!file) {
        return;
      }

      setSelectedFile(
        file
      );


      /*
       * Contrôle qualité local :
       *
       * - résolution
       * - cadrage
       * - luminosité
       * - flou
       * - orientation
       * - présence de contenu
       *
       * Le traitement détaillé sera fourni par
       * components.tsx / logique caméra du frontend.
       */

      const qualityResult =
        await localQualityCheck(
          file
        );

      setQuality(
        qualityResult
      );

    } catch (error) {

      console.log(
        "Input selection:",
        error
      );
    }
  }


  async function submitHelp(
    direct: boolean
  ) {

    if (
      inputMode === "text" &&
      !exerciseText.trim()
    ) {
      return;
    }

    if (
      inputMode !== "text" &&
      !selectedFile
    ) {
      return;
    }


    setLoading(
      true
    );

    setDirectSolution(
      direct
    );

    setHintLevel(
      direct
        ? 4
        : 1
    );

    setMessages(
      []
    );


    try {

      /*
       * Le backend effectue :
       *
       * 1. validation
       * 2. contrôle anti-abus
       * 3. vérification crédit
       * 4. traitement Gemini
       * 5. streaming
       *
       * Les images ont déjà été contrôlées localement.
       */

      const result =
        await startHelpRequest({
          mode:
            inputMode,

          text:
            exerciseText,

          file:
            selectedFile,

          direct,
        });


      if (
        result?.conversationId
      ) {

        setConversationId(
          result.conversationId
        );
      }


      if (
        result?.credits
      ) {

        onCreditsChange(
          result.credits
        );
      }


      if (
        result?.history
      ) {

        onHistoryChange(
          result.history
        );
      }

    } catch (error) {

      setMessages(
        previous => [
          ...previous,
          {
            id:
              createId(),

            role:
              "assistant",

            content:
              getErrorMessage(
                error
              ),
          },
        ]
      );

    } finally {

      setLoading(
        false
      );
    }
  }


  /*
   * Indices 1 → 2 → 3.
   *
   * L'utilisateur ne reçoit jamais les trois
   * indices automatiquement.
   */

  async function requestNextHint() {

    if (
      hintLevel >= 3 ||
      !conversationId ||
      streaming
    ) {
      return;
    }

    const nextLevel =
      hintLevel + 1;

    setStreaming(
      true
    );


    const assistantId =
      createId();


    setMessages(
      previous => [
        ...previous,
        {
          id:
            assistantId,

          role:
            "assistant",

          content:
            "",
        },
      ]
    );


    try {

      await streamEndpoint(
        `${API_URL}/api/help/hint`,

        {
          conversation_id:
            conversationId,

          level:
            nextLevel,
        },

        chunk => {

          setMessages(
            previous =>
              previous.map(
                message =>
                  message.id ===
                  assistantId
                    ? {
                        ...message,
                        content:
                          message.content +
                          chunk,
                      }
                    : message
              )
          );

        },

        () => {

          setHintLevel(
            nextLevel
          );

          setStreaming(
            false
          );
        }
      );

    } catch (error) {

      setStreaming(
        false
      );

      console.log(
        "Hint streaming:",
        error
      );
    }
  }


  async function askQuestion() {

    if (
      !answer.trim() ||
      !conversationId ||
      streaming
    ) {
      return;
    }

    const question =
      answer.trim();

    setAnswer("");


    const userId =
      createId();

    const assistantId =
      createId();


    setMessages(
      previous => [
        ...previous,

        {
          id:
            userId,

          role:
            "user",

          content:
            question,
        },

        {
          id:
            assistantId,

          role:
            "assistant",

          content:
            "",
        },
      ]
    );


    setStreaming(
      true
    );


    try {

      await streamEndpoint(
        `${API_URL}/api/help/question`,

        {
          conversation_id:
            conversationId,

          question,
        },

        chunk => {

          setMessages(
            previous =>
              previous.map(
                message =>
                  message.id ===
                  assistantId
                    ? {
                        ...message,
                        content:
                          message.content +
                          chunk,
                      }
                    : message
              )
          );

        },

        () => {

          setStreaming(
            false
          );
        }
      );

    } catch (error) {

      setStreaming(
        false
      );

      console.log(
        "Question streaming:",
        error
      );
    }
  }


  return (
    <KeyboardAvoidingView
      style={
        styles.screen
      }
      behavior={
        Platform.OS ===
        "ios"
          ? "padding"
          : undefined
      }
    >

      <ScrollView
        showsVerticalScrollIndicator={
          false
        }
        contentContainerStyle={
          styles.scrollContent
        }
      >

        <View
          style={
            styles.hero
          }
        >

          <View
            style={
              styles.heroBadge
            }
          >

            <Sparkles
              size={14}
              color={
                COLORS.primary
              }
            />

            <Text
              style={
                styles.heroBadgeText
              }
            >
              Assistant pédagogique
            </Text>

          </View>


          <Text
            style={
              styles.heroTitle
            }
          >
            Bloqué sur un exercice ?
          </Text>


          <Text
            style={
              styles.heroDescription
            }
          >
            Envoie ton exercice et avance avec
            des indices progressifs jusqu'à
            comprendre par toi-même.
          </Text>

        </View>


        <Card>

          <Text
            style={
              styles.cardTitle
            }
          >
            Ton exercice
          </Text>


          <SourceSelector
            value={
              inputMode
            }
            onChange={
              selectInput
            }
          />


          {inputMode ===
            "text" && (

            <TextInput
              value={
                exerciseText
              }
              onChangeText={
                setExerciseText
              }
              placeholder={
                "Écris ou colle l'énoncé de ton exercice..."
              }
              placeholderTextColor={
                COLORS.muted
              }
              multiline
              textAlignVertical="top"
              style={
                styles.exerciseInput
              }
            />

          )}


          {inputMode !==
            "text" && (

            <Pressable
              onPress={() =>
                selectInput(
                  inputMode
                )
              }
              style={
                styles.uploadZone
              }
            >

              {inputMode ===
                "camera" ? (

                <Camera
                  size={34}
                  color={
                    COLORS.primary
                  }
                />

              ) : inputMode ===
                "pdf" ? (

                <FileText
                  size={34}
                  color={
                    COLORS.primary
                  }
                />

              ) : (

                <ImageIcon
                  size={34}
                  color={
                    COLORS.primary
                  }
                />

              )}


              <Text
                style={
                  styles.uploadTitle
                }
              >
                {selectedFile
                  ? "Fichier sélectionné"
                  : "Ajouter ton document"}
              </Text>


              <Text
                style={
                  styles.uploadDescription
                }
              >
                {selectedFile
                  ? selectedFile.name ||
                    "Document prêt"
                  : "Photo, caméra ou PDF"}
              </Text>


              <Upload
                size={18}
                color={
                  COLORS.muted
                }
              />

            </Pressable>

          )}


          {quality && (

            <QualityBadge
              result={
                quality
              }
            />

          )}


          <View
            style={
              styles.actionStack
            }
          >

            <AppButton
              title={
                loading
                  ? "Analyse en cours..."
                  : directSolution
                    ? "Résolution directe"
                    : "Obtenir un indice"
              }
              icon={
                loading
                  ? undefined
                  : <Lightbulb
                      size={19}
                      color="#fff"
                    />
              }
              loading={
                loading
              }
              onPress={() =>
                submitHelp(
                  false
                )
              }
            />


            <AppButton
              title="Résolution complète"
              variant="secondary"
              onPress={() =>
                submitHelp(
                  true
                )
              }
            />

          </View>

        </Card>


        {messages.length >
          0 && (

          <Card>

            <View
              style={
                styles.resultHeader
              }>

              <View>

                <Text
                  style={
                    styles.cardTitle
                  }
                >
                  Accompagnement
                </Text>

                <Text
                  style={
                    styles.resultSubtitle
                  }
                >
                  {directSolution
                    ? "Résolution complète"
                    : `Indice ${Math.min(
                        hintLevel,
                        3
                      )} sur 3`}
                </Text>

              </View>


              <CheckCircle
                size={22}
                color={
                  COLORS.success
                }
              />

            </View>


            {messages.map(
              message => (

                <MessageBubble
                  key={
                    message.id
                  }
                  role={
                    message.role
                  }
                  content={
                    message.content
                  }
                />

              )
            )}


            {!directSolution &&
              hintLevel <
                3 && (

              <AppButton
                title={
                  `Afficher l'indice ${
                    hintLevel + 1
                  }`
                }
                icon={
                  <Lightbulb
                    size={18}
                    color="#fff"
                  />
                }
                loading={
                  streaming
                }
                onPress={
                  requestNextHint
                }
              />

            )}


            {!directSolution &&
              hintLevel >=
                3 && (

              <View
                style={
                  styles.completeHint
                }
              >

                <CheckCircle
                  size={18}
                  color={
                    COLORS.success
                  }
                />

                <Text
                  style={
                    styles.completeHintText
                  }
                >
                  Les 3 indices ont été affichés.
                  Tu peux maintenant demander
                  la résolution complète.
                </Text>

              </View>

            )}


            <View
              style={
                styles.questionBox
              }
            >

              <Text
                style={
                  styles.questionTitle
                }
              >
                Tu as une question ?
              </Text>


              <View
                style={
                  styles.questionRow
                }
              >

                <TextInput
                  value={
                    answer
                  }
                  onChangeText={
                    setAnswer
                  }
                  placeholder={
                    "Pose ta question..."
                  }
                  placeholderTextColor={
                    COLORS.muted
                  }
                  style={
                    styles.questionInput
                  }
                  editable={
                    !streaming
                  }
                />


                <Pressable
                  disabled={
                    streaming
                  }
                  onPress={
                    askQuestion
                  }
                  style={
                    styles.sendButton
                  }
                >

                  <Send
                    size={18}
                    color="#fff"
                  />

                </Pressable>

              </View>

            </View>

          </Card>

        )}


        <View
          style={
            styles.creditInfo
          }
        >

          <Zap
            size={15}
            color={
              COLORS.warning
            }
          />

          <Text
            style={
              styles.creditInfoText
            }
          >
            {credits.balance} crédit
            {credits.balance !==
            1
              ? "s"
              : ""} disponible
            {credits.balance !==
            1
              ? "s"
              : ""}
          </Text>

        </View>

      </ScrollView>

    </KeyboardAvoidingView>
  );
}


/* ============================================================
   LEARN A COMPETENCE
   ============================================================ */

function LearnScreen({
  credits,
  onCreditsChange,
}: {
  credits: Credits;
  onCreditsChange: (
    credits: Credits
  ) => void;
}) {

  const [concept, setConcept] =
    useState("");

  const [understanding, setUnderstanding] =
    useState("");

  const [referenceExercises, setReferenceExercises] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [lesson, setLesson] =
    useState<any>(null);

  const [question, setQuestion] =
    useState("");

  const [messages, setMessages] =
    useState<Message[]>([]);

  const [streaming, setStreaming] =
    useState(false);


  async function startLearning() {

    if (
      !concept.trim()
    ) {
      return;
    }

    setLoading(
      true
    );

    try {

      const response =
        await startLearnRequest({
          concept:
            concept.trim(),

          understanding:
            understanding.trim(),

          exercises:
            referenceExercises.trim(),
        });


      setLesson(
        response
      );


      if (
        response?.credits
      ) {

        onCreditsChange(
          response.credits
        );
      }

    } catch (error) {

      setLesson({
        error:
          getErrorMessage(
            error
          ),
      });

    } finally {

      setLoading(
        false
      );
    }
  }


  async function askQuestion() {

    if (
      !question.trim() ||
      !lesson?.lessonId ||
      streaming
    ) {
      return;
    }

    const current =
      question.trim();

    setQuestion("");

    const userId =
      createId();

    const assistantId =
      createId();

    setMessages(
      previous => [
        ...previous,

        {
          id:
            userId,

          role:
            "user",

          content:
            current,
        },

        {
          id:
            assistantId,

          role:
            "assistant",

          content:
            "",
        },
      ]
    );


    setStreaming(
      true
    );


    try {

      await streamEndpoint(
        `${API_URL}/api/learn/question`,

        {
          lesson_id:
            lesson.lessonId,

          question:
            current,
        },

        chunk => {

          setMessages(
            previous =>
              previous.map(
                message =>
                  message.id ===
                  assistantId
                    ? {
                        ...message,
                        content:
                          message.content +
                          chunk,
                      }
                    : message
              )
          );

        },

        () => {

          setStreaming(
            false
          );

        }
      );

    } catch (error) {

      setStreaming(
        false
      );

      console.log(
        "Learn question:",
        error
      );
    }
  }


  return (
    <KeyboardAvoidingView
      style={
        styles.screen
      }
      behavior={
        Platform.OS ===
        "ios"
          ? "padding"
          : undefined
      }
    >

      <ScrollView
        showsVerticalScrollIndicator={
          false
        }
        contentContainerStyle={
          styles.scrollContent
        }
      >

        <View
          style={
            styles.hero
          }
        >

          <View
            style={
              styles.heroBadge
            }
          >

            <BookOpen
              size={14}
              color={
                COLORS.primary
              }
            />

            <Text
              style={
                styles.heroBadgeText
              }
            >
              Learn a competence
            </Text>

          </View>


          <Text
            style={
              styles.heroTitle
            }
          >
            Maîtrise vraiment un concept
          </Text>


          <Text
            style={
              styles.heroDescription
            }
          >
            HintAI t'explique le concept puis te
            propose deux exercices : un accessible
            et un défi très avancé.
          </Text>

        </View>


        <Card>

          <Text
            style={
              styles.cardTitle
            }
          >
            Nouveau parcours
          </Text>


          <Text
            style={
              styles.label
            }
          >
            Concept à apprendre
          </Text>

          <TextInput
            value={
              concept
            }
            onChangeText={
              setConcept
            }
            placeholder={
              "Ex : dérivées, probabilités, lois de Newton..."
            }
            placeholderTextColor={
              COLORS.muted
            }
            style={
              styles.singleInput
            }
          />


          <Text
            style={
              styles.label
            }
          >
            Ce que tu as déjà compris
            <Text
              style={
                styles.optional
              }
            >
              {" "}— optionnel
            </Text>
          </Text>

          <TextInput
            value={
              understanding
            }
            onChangeText={
              setUnderstanding
            }
            placeholder={
              "Explique ce que tu sais déjà..."
            }
            placeholderTextColor={
              COLORS.muted
            }
            multiline
            textAlignVertical="top"
            style={
              styles.textArea
            }
          />


          <Text
            style={
              styles.label
            }
          >
            Exercices de référence
            <Text
              style={
                styles.optional
              }
            >
              {" "}— jusqu'à 3, optionnel
            </Text>
          </Text>

          <TextInput
            value={
              referenceExercises
            }
            onChangeText={
              setReferenceExercises
            }
            placeholder={
              "Ajoute des exercices similaires si tu en as..."
            }
            placeholderTextColor={
              COLORS.muted
            }
            multiline
            textAlignVertical="top"
            style={
              styles.textArea
            }
          />


          <AppButton
            title="Commencer l'apprentissage"
            icon={
              <Sparkles
                size={18}
                color="#fff"
              />
            }
            loading={
              loading
            }
            onPress={
              startLearning
            }
          />

        </Card>


        {lesson && (

          <Card>

            {lesson.error ? (

              <View
                style={
                  styles.errorBox
                }
              >

                <AlertCircle
                  size={20}
                  color={
                    COLORS.error
                  }
                />

                <Text
                  style={
                    styles.errorText
                  }
                >
                  {lesson.error}
                </Text>

              </View>

            ) : (

              <>

                <Text
                  style={
                    styles.cardTitle
                  }
                >
                  Comprendre le concept
                </Text>


                {lesson.explanation && (

                  <Text
                    style={
                      styles.explanation
                    }
                  >
                    {lesson.explanation}
                  </Text>

                )}


                {lesson.exercise1 && (

                  <ExerciseCard
                    number="01"
                    title="Exercice progressif"
                    content={
                      lesson.exercise1
                    }
                  />

                )}


                {lesson.exercise2 && (

                  <ExerciseCard
                    number="02"
                    title="Défi avancé"
                    content={
                      lesson.exercise2
                    }
                  />

                )}


                <View
                  style={
                    styles.questionBox
                  }
                >

                  <Text
                    style={
                      styles.questionTitle
                    }
                  >
                    Une question sur le concept ?
                  </Text>


                  {messages.map(
                    message => (

                      <MessageBubble
                        key={
                          message.id
                        }
                        role={
                          message.role
                        }
                        content={
                          message.content
                        }
                      />

                    )
                  )}


                  <View
                    style={
                      styles.questionRow
                    }
                  >

                    <TextInput
                      value={
                        question
                      }
                      onChangeText={
                        setQuestion
                      }
                      placeholder={
                        "Pose ta question..."
                      }
                      placeholderTextColor={
                        COLORS.muted
                      }
                      style={
                        styles.questionInput
                      }
                    />

                    <Pressable
                      disabled={
                        streaming
                      }
                      onPress={
                        askQuestion
                      }
                      style={
                        styles.sendButton
                      }
                    >

                      <Send
                        size={18}
                        color="#fff"
                      />

                    </Pressable>

                  </View>

                </View>

              </>

            )}

          </Card>

        )}


        <View
          style={
            styles.creditInfo
          }
        >

          <Zap
            size={15}
            color={
              COLORS.warning
            }
          />

          <Text
            style={
              styles.creditInfoText
            }
          >
            {credits.balance} crédits disponibles
          </Text>

        </View>

      </ScrollView>

    </KeyboardAvoidingView>
  );
}


/* ============================================================
   HISTORIQUE
   ============================================================ */

function HistoryScreen({
  history,
}: {
  history: HistoryItem[];
}) {

  return (
    <ScrollView
      showsVerticalScrollIndicator={
        false
      }
      contentContainerStyle={
        styles.scrollContent
      }
    >

      <View
        style={
          styles.pageHeader
        }
      >

        <View
          style={
            styles.heroBadge
          }
        >

          <History
            size={14}
            color={
              COLORS.primary
            }
          />

          <Text
            style={
              styles.heroBadgeText
            }
          >
            Mémoire locale
          </Text>

        </View>


        <Text
          style={
            styles.pageTitle
          }
        >
          Ton historique
        </Text>


        <Text
          style={
            styles.pageDescription
          }
        >
          Tes activités sont conservées localement
          pour pouvoir retrouver facilement tes
          exercices.
        </Text>

      </View>


      {history.length ===
        0 ? (

        <EmptyState
          icon={
            <History
              size={36}
              color={
                COLORS.muted
              }
            />
          }
          title="Aucune activité"
          description="Tes exercices et parcours apparaîtront ici."
        />

      ) : (

        history.map(
          item => (

            <Card
              key={
                item.id
              }
            >

              <View
                style={
                  styles.historyRow
                }
              >

                <View
                  style={
                    styles.historyIcon
                  }
                >

                  {item.type ===
                  "help" ? (

                    <Lightbulb
                      size={19}
                      color={
                        COLORS.primary
                      }
                    />

                  ) : (

                    <BookOpen
                      size={19}
                      color={
                        COLORS.primary
                      }
                    />

                  )}

                </View>


                <View
                  style={
                    styles.historyContent
                  }
                >

                  <Text
                    style={
                      styles.historyTitle
                    }
                  >
                    {item.title}
                  </Text>

                  <Text
                    style={
                      styles.historyDate
                    }
                  >
                    {item.date}
                  </Text>

                </View>


                <ChevronRight
                  size={19}
                  color={
                    COLORS.muted
                  }
                />

              </View>

            </Card>

          )
        )

      )}

    </ScrollView>
  );
}


/* ============================================================
   PROFIL / ABONNEMENT
   ============================================================ */

function ProfileScreen({
  user,
  credits,
  onUserChange,
}: {
  user: User | null;
  credits: Credits;
  onUserChange: (
    user: User | null
  ) => void;
}) {

  const [loadingPlan, setLoadingPlan] =
    useState(false);


  async function subscribe(
    plan: UserPlan
  ) {

    if (
      plan ===
      user?.plan
    ) {
      return;
    }

    setLoadingPlan(
      true
    );

    try {

      /*
       * Le backend crée la session de paiement.
       * Le frontend ne modifie jamais directement
       * l'abonnement.
       */

      const response =
        await fetch(
          `${API_URL}/api/subscriptions/checkout`,
          {
            method:
              "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body:
              JSON.stringify({
                plan,
              }),
          }
        );


      if (!response.ok) {
        throw new Error(
          "Impossible de créer le paiement."
        );
      }


      const data =
        await response.json();


      /*
       * Le backend retournera l'URL de paiement.
       * L'ouverture du navigateur sera branchée
       * avec Expo Linking.
       */

      if (
        data?.checkout_url
      ) {

        console.log(
          "Checkout:",
          data.checkout_url
        );
      }

    } catch (error) {

      console.log(
        "Subscription:",
        error
      );

    } finally {

      setLoadingPlan(
        false
      );
    }
  }


  return (
    <ScrollView
      showsVerticalScrollIndicator={
        false
      }
      contentContainerStyle={
        styles.scrollContent
      }
    >

      <View
        style={
          styles.profileTop
        }
      >

        <View
          style={
            styles.profileAvatar
          }
        >

          <User
            size={32}
            color={
              COLORS.primary
            }
          />

        </View>


        <Text
          style={
            styles.profileName
          }
        >
          {
            user?.name ||
            "Utilisateur HintAI"
          }
        </Text>


        <Text
          style={
            styles.profileEmail
          }
        >
          {
            user?.email ||
            "Compte local"
          }
        </Text>

      </View>


      <Card>

        <View
          style={
            styles.creditHeader
          }
        >

          <View>

            <Text
              style={
                styles.creditLabel
              }
            >
              Crédits disponibles
            </Text>

            <Text
              style={
                styles.creditBig
              }
            >
              {credits.balance}
            </Text>

          </View>


          <View
            style={
              styles.creditIconLarge
            }
          >

            <Zap
              size={26}
              color={
                COLORS.warning
              }
            />

          </View>

        </View>

      </Card>


      <View
        style={
          styles.sectionHeader
        }
      >

        <Crown
          size={19}
          color={
            COLORS.warning
          }
        />

        <Text
          style={
            styles.sectionTitle
          }
        >
          Abonnement
        </Text>

      </View>


      {PLANS.map(
        plan => (

          <PlanCard
            key={
              plan.id
            }
            plan={
              plan
            }
            active={
              user?.plan ===
              plan.id
            }
            loading={
              loadingPlan
            }
            onPress={() =>
              subscribe(
                plan.id
              )
            }
          />

        )
      )}


      <View
        style={
          styles.adsNotice
        }
      >

        <Text
          style={
            styles.adsNoticeText
          }
        >
          Les offres peuvent inclure des publicités
          et des publicités récompensées selon les
          règles du plan.
        </Text>

      </View>


      <Pressable
        onPress={() =>
          onUserChange(
            null
          )
        }
        style={
          styles.logoutButton
        }
      >

        <Text
          style={
            styles.logoutText
          }
        >
          Se déconnecter
        </Text>

      </Pressable>

    </ScrollView>
  );
}


/* ============================================================
   API HELPERS
   ============================================================ */

/*
 * Ces helpers restent dans App.tsx conformément à
 * l'arborescence de 3 fichiers.
 *
 * Plus tard, si nous décidons de déplacer ces appels,
 * nous ne créerons PAS un quatrième fichier :
 * ils pourront être regroupés dans components.tsx
 * ou dans App.tsx.
 */


/* ------------------------------------------------------------
   SESSION
   ------------------------------------------------------------ */

async function getSession() {

  /*
   * TODO backend :
   *
   * GET /api/auth/me
   *
   * Pour le moment, on évite de bloquer l'application
   * si le backend n'est pas encore configuré.
   */

  try {

    const response =
      await fetch(
        `${API_URL}/api/auth/me`
      );

    if (
      !response.ok
    ) {
      return null;
    }

    return await response.json();

  } catch {

    return null;
  }
}


/* ------------------------------------------------------------
   HELP ME
   ------------------------------------------------------------ */

async function startHelpRequest({
  mode,
  text,
  file,
  direct,
}: {
  mode: InputMode;
  text: string;
  file: any;
  direct: boolean;
}) {

  const form =
    new FormData();


  form.append(
    "mode",
    mode
  );

  form.append(
    "direct",
    String(
      direct
    )
  );


  if (
    text.trim()
  ) {

    form.append(
      "text",
      text.trim()
    );
  }


  if (
    file
  ) {

    form.append(
      "file",
      file
    );
  }


  const response =
    await fetch(
      `${API_URL}/api/help`,
      {
        method:
          "POST",

        body:
          form,
      }
    );


  if (
    !response.ok
  ) {

    const message =
      await safeResponseMessage(
        response
      );

    throw new Error(
      message
    );
  }


  return await response.json();
}


/* ------------------------------------------------------------
   LEARN
   ------------------------------------------------------------ */

async function startLearnRequest({
  concept,
  understanding,
  exercises,
}: {
  concept: string;
  understanding: string;
  exercises: string;
}) {

  const response =
    await fetch(
      `${API_URL}/api/learn`,
      {
        method:
          "POST",

        headers: {
          "Content-Type":
            "application/json",
        },

        body:
          JSON.stringify({
            concept,
            understanding,
            exercises,
          }),
      }
    );


  if (
    !response.ok
  ) {

    const message =
      await safeResponseMessage(
        response
      );

    throw new Error(
      message
    );
  }


  return await response.json();
}


/* ------------------------------------------------------------
   STREAMING SSE
   ------------------------------------------------------------ */

async function streamEndpoint(
  url: string,
  body: Record<string, any>,
  onChunk: (
    chunk: string
  ) => void,
  onComplete: () => void
) {

  const response =
    await fetch(
      url,
      {
        method:
          "POST",

        headers: {
          "Content-Type":
            "application/json",

          Accept:
            "text/event-stream",
        },

        body:
          JSON.stringify(
            body
          ),
      }
    );


  if (
    !response.ok
  ) {

    throw new Error(
      await safeResponseMessage(
        response
      )
    );
  }


  /*
   * React Native / Expo modernes exposent
   * response.body comme ReadableStream.
   */

  if (
    !response.body
  ) {

    /*
     * Fallback si le runtime ne fournit pas
     * ReadableStream.
     */

    const text =
      await response.text();

    parseSSE(
      text,
      onChunk
    );

    onComplete();

    return;
  }


  const reader =
    response.body.getReader();

  const decoder =
    new TextDecoder(
      "utf-8"
    );

  let buffer =
    "";


  while (true) {

    const {
      done,
      value,
    } =
      await reader.read();


    if (
      done
    ) {

      break;
    }


    buffer +=
      decoder.decode(
        value,
        {
          stream:
            true,
        }
      );


    const events =
      buffer.split(
        "\n\n"
      );


    buffer =
      events.pop() ||
      "";


    for (
      const event
      of events
    ) {

      parseSSE(
        event,
        onChunk
      );
    }
  }


  if (
    buffer.trim()
  ) {

    parseSSE(
      buffer,
      onChunk
    );
  }


  onComplete();
}


/* ------------------------------------------------------------
   PARSE SSE
   ------------------------------------------------------------ */

function parseSSE(
  raw: string,
  onChunk: (
    chunk: string
  ) => void
) {

  const lines =
    raw.split(
      "\n"
    );


  for (
    const line
    of lines
  ) {

    if (
      !line.startsWith(
        "data:"
      )
    ) {
      continue;
    }


    const payload =
      line
        .slice(5)
        .trim();


    if (
      !payload
    ) {
      continue;
    }


    if (
      payload ===
      "[DONE]"
    ) {
      continue;
    }


    try {

      const data =
        JSON.parse(
          payload
        );


      if (
        data.done
      ) {
        continue;
      }


      if (
        typeof data.text ===
        "string"
      ) {

        onChunk(
          data.text
        );

      } else if (
        typeof data.content ===
        "string"
      ) {

        onChunk(
          data.content
        );

      } else if (
        typeof data.chunk ===
        "string"
      ) {

        onChunk(
          data.chunk
        );
      }

    } catch {

      /*
       * Certains serveurs SSE peuvent envoyer
       * directement du texte.
       */

      onChunk(
        payload
      );
    }
  }
}


/* ============================================================
   STOCKAGE LOCAL
   ============================================================ */

async function loadLocalHistory(): Promise<
  HistoryItem[]
> {

  /*
   * Pour Expo, le stockage persistant sera branché
   * avec AsyncStorage.
   *
   * On utilise globalThis.localStorage lorsqu'il est
   * disponible, ce qui permet également de conserver
   * la compatibilité web.
   */

  try {

    const storage =
      (
        globalThis as any
      ).localStorage;


    if (
      !storage
    ) {
      return [];
    }


    const raw =
      storage.getItem(
        "hintai_history"
      );


    if (
      !raw
    ) {
      return [];
    }


    const parsed =
      JSON.parse(
        raw
      );


    return Array.isArray(
      parsed
    )
      ? parsed
      : [];

  } catch {

    return [];
  }
}


/* ============================================================
   FICHIERS / CAMERA
   ============================================================ */

async function pickInput(
  mode: InputMode
) {

  /*
   * Le traitement caméra/document reste local.
   *
   * Les APIs Expo ImagePicker / DocumentPicker /
   * Camera seront utilisées ici.
   *
   * Le contrôle OpenCV.js intervient avant l'envoi
   * au backend.
   *
   * Cette fonction est volontairement isolée afin
   * que le reste de l'interface ne dépende pas
   * du mécanisme de sélection.
   */

  console.log(
    "Input requested:",
    mode
  );

  return null;
}


/* ============================================================
   CONTRÔLE QUALITÉ LOCAL
   ============================================================ */

async function localQualityCheck(
  file: any
) {

  /*
   * Pipeline prévu :
   *
   * 1. lecture de l'image
   * 2. détection des contours
   * 3. cadrage
   * 4. correction perspective
   * 5. luminosité
   * 6. contraste
   * 7. netteté / flou
   * 8. vérification du contenu
   *
   * Le backend ne doit recevoir l'image qu'après
   * validation locale.
   */

  if (
    !file
  ) {

    return {
      valid:
        false,

      score:
        0,

      message:
        "Aucune image sélectionnée.",
    };
  }


  /*
   * Placeholder jusqu'au branchement réel
   * d'OpenCV.js.
   */

  return {
    valid:
      true,

    score:
      1,

    message:
      "Document prêt pour l'analyse.",
  };
}


/* ============================================================
   UTILITAIRES
   ============================================================ */

function createId(): string {

  return (
    `${Date.now()}_` +
    `${Math.random()
      .toString(36)
      .slice(2, 10)}`
  );
}


function getErrorMessage(
  error: unknown
): string {

  if (
    error instanceof Error
  ) {

    return error.message;
  }

  return (
    "Une erreur est survenue. Réessaie."
  );
}


async function safeResponseMessage(
  response: Response
): Promise<string> {

  try {

    const data =
      await response.json();


    return (
      data?.error?.message ||
      data?.message ||
      "Une erreur est survenue."
    );

  } catch {

    return (
      `Erreur serveur (${response.status}).`
    );
  }
}
```
