```tsx
/**
 * HintAI
 * frontend/components.tsx
 *
 * Composants UI réutilisables de l'application.
 *
 * Structure frontend définitive :
 *
 * frontend/
 * ├── App.tsx
 * ├── components.tsx
 * └── styles.ts
 */

import React from "react";

import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  Text,
  View,
} from "react-native";

import {
  Camera,
  CheckCircle,
  FileText,
  Image as ImageIcon,
  Lightbulb,
  BookOpen,
  History,
  User,
  Sparkles,
  ChevronRight,
  AlertCircle,
  Upload,
  Zap,
  Crown,
  MessageCircle,
  Send,
} from "lucide-react-native";

import {
  styles,
  COLORS,
} from "./styles";


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

type Plan = {
  id:
    | "free"
    | "basic"
    | "pro"
    | "proplus"
    | "super"
    | "heavy";

  name: string;

  price: string;

  description: string;
};


/* ============================================================
   APP BUTTON
   ============================================================ */

export function AppButton({
  title,
  onPress,
  variant = "primary",
  loading = false,
  disabled = false,
  icon,
}: {
  title: string;

  onPress: () => void;

  variant?:
    | "primary"
    | "secondary"
    | "danger"
    | "ghost";

  loading?: boolean;

  disabled?: boolean;

  icon?: React.ReactNode;
}) {

  const isDisabled =
    disabled ||
    loading;


  return (
    <Pressable
      disabled={
        isDisabled
      }
      onPress={
        onPress
      }
      style={({
        pressed,
      }) => [
        styles.button,

        variant ===
          "primary" &&
          styles.buttonPrimary,

        variant ===
          "secondary" &&
          styles.buttonSecondary,

        variant ===
          "danger" &&
          styles.buttonDanger,

        variant ===
          "ghost" &&
          styles.buttonGhost,

        pressed &&
          !isDisabled &&
          styles.buttonPressed,

        isDisabled &&
          styles.buttonDisabled,
      ]}
    >

      {loading ? (

        <ActivityIndicator
          size="small"
          color={
            variant ===
            "secondary"
              ? COLORS.primary
              : "#FFFFFF"
          }
        />

      ) : (

        <>
          {icon}

          <Text
            style={[
              styles.buttonText,

              variant ===
                "secondary" &&
                styles.buttonTextSecondary,

              variant ===
                "ghost" &&
                styles.buttonTextGhost,
            ]}
          >
            {title}
          </Text>
        </>

      )}

    </Pressable>
  );
}


/* ============================================================
   CARD
   ============================================================ */

export function Card({
  children,
  style,
}: {
  children:
    React.ReactNode;

  style?: any;
}) {

  return (
    <View
      style={[
        styles.card,
        style,
      ]}
    >
      {children}
    </View>
  );
}


/* ============================================================
   SOURCE SELECTOR
   ============================================================ */

export function SourceSelector({
  value,
  onChange,
}: {
  value:
    InputMode;

  onChange: (
    mode: InputMode
  ) => void;
}) {

  const options: {
    id: InputMode;
    label: string;
    icon: React.ReactNode;
  }[] = [

    {
      id: "text",
      label: "Texte",
      icon: (
        <MessageCircle
          size={18}
        />
      ),
    },

    {
      id: "camera",
      label: "Caméra",
      icon: (
        <Camera
          size={18}
        />
      ),
    },

    {
      id: "image",
      label: "Photo",
      icon: (
        <ImageIcon
          size={18}
        />
      ),
    },

    {
      id: "pdf",
      label: "PDF",
      icon: (
        <FileText
          size={18}
        />
      ),
    },

  ];


  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={
        false
      }
      contentContainerStyle={
        styles.sourceSelector
      }
    >

      {options.map(
        option => {

          const active =
            value ===
            option.id;


          return (
            <Pressable
              key={
                option.id
              }
              onPress={() =>
                onChange(
                  option.id
                )
              }
              style={[
                styles.sourceButton,

                active &&
                  styles.sourceButtonActive,
              ]}
            >

              {React.cloneElement(
                option.icon as React.ReactElement,
                {
                  color:
                    active
                      ? "#FFFFFF"
                      : COLORS.textSecondary,
                }
              )}

              <Text
                style={[
                  styles.sourceButtonText,

                  active &&
                    styles.sourceButtonTextActive,
                ]}
              >
                {option.label}
              </Text>

            </Pressable>
          );

        }
      )}

    </ScrollView>
  );
}


/* ============================================================
   QUALITY BADGE
   ============================================================ */

export function QualityBadge({
  result,
}: {
  result: {
    valid?: boolean;
    score?: number;
    message?: string;
  };
}) {

  const valid =
    result.valid !==
    false;


  return (
    <View
      style={[
        styles.qualityBadge,

        valid
          ? styles.qualitySuccess
          : styles.qualityError,
      ]}
    >

      {valid ? (

        <CheckCircle
          size={18}
          color={
            COLORS.success
          }
        />

      ) : (

        <AlertCircle
          size={18}
          color={
            COLORS.error
          }
        />

      )}


      <View
        style={
          styles.qualityContent
        }
      >

        <Text
          style={
            styles.qualityTitle
          }
        >
          {valid
            ? "Document validé"
            : "Qualité insuffisante"}
        </Text>

        <Text
          style={
            styles.qualityMessage
          }
        >
          {
            result.message ||
            (
              valid
                ? "L'image peut être analysée."
                : "Améliore l'image avant de continuer."
            )
          }
        </Text>

      </View>


      {typeof result.score ===
        "number" && (

        <Text
          style={
            styles.qualityScore
          }
        >
          {Math.round(
            result.score *
              100
          )}
          %
        </Text>

      )}

    </View>
  );
}


/* ============================================================
   LOADING VIEW
   ============================================================ */

export function LoadingView({
  title = "Analyse en cours...",
  description = "HintAI prépare ta réponse.",
}: {
  title?: string;

  description?: string;
}) {

  return (
    <View
      style={
        styles.loadingBox
      }
    >

      <View
        style={
          styles.loadingIcon
        }
      >

        <Sparkles
          size={25}
          color={
            COLORS.primary
          }
        />

      </View>


      <ActivityIndicator
        size="large"
        color={
          COLORS.primary
        }
      />


      <Text
        style={
          styles.loadingBoxTitle
        }
      >
        {title}
      </Text>


      <Text
        style={
          styles.loadingBoxDescription
        }
      >
        {description}
      </Text>

    </View>
  );
}


/* ============================================================
   MESSAGE BUBBLE
   ============================================================ */

export function MessageBubble({
  role,
  content,
}: {
  role:
    | "user"
    | "assistant";

  content: string;
}) {

  const isUser =
    role ===
    "user";


  return (
    <View
      style={[
        styles.messageContainer,

        isUser &&
          styles.messageContainerUser,
      ]}
    >

      <View
        style={[
          styles.messageBubble,

          isUser
            ? styles.userBubble
            : styles.assistantBubble,
        ]}
      >

        <View
          style={
            styles.messageHeader
          }
        >

          {isUser ? (

            <User
              size={15}
              color={
                COLORS.primary
              }
            />

          ) : (

            <Sparkles
              size={15}
              color={
                COLORS.primary
              }
            />

          )}


          <Text
            style={
              styles.messageAuthor
            }
          >
            {isUser
              ? "Toi"
              : "HintAI"}
          </Text>

        </View>


        {content ? (

          <Text
            style={
              styles.messageText
            }
          >
            {content}
          </Text>

        ) : (

          <View
            style={
              styles.typingIndicator
            }
          >

            <View
              style={
                styles.typingDot
              }
            />

            <View
              style={
                styles.typingDot
              }
            />

            <View
              style={
                styles.typingDot
              }
            />

          </View>

        )}

      </View>

    </View>
  );
}


/* ============================================================
   EXERCISE CARD
   ============================================================ */

export function ExerciseCard({
  number,
  title,
  content,
}: {
  number: string;

  title: string;

  content: string;
}) {

  return (
    <View
      style={
        styles.exerciseCard
      }
    >

      <View
        style={
          styles.exerciseHeader
        }
      >

        <View
          style={
            styles.exerciseNumber
          }
        >

          <Text
            style={
              styles.exerciseNumberText
            }
          >
            {number}
          </Text>

        </View>


        <View
          style={
            styles.exerciseHeaderContent
          }
        >

          <Text
            style={
              styles.exerciseTitle
            }
          >
            {title}
          </Text>

          <Text
            style={
              styles.exerciseSubtitle
            }
          >
            Essaie avant de regarder la correction.
          </Text>

        </View>

      </View>


      <Text
        style={
          styles.exerciseContent
        }
      >
        {content}
      </Text>


      <View
        style={
          styles.exerciseFooter
        }
      >

        <Lightbulb
          size={16}
          color={
            COLORS.warning
          }
        />

        <Text
          style={
            styles.exerciseFooterText
          }
        >
          Tu peux demander un indice si nécessaire.
        </Text>

      </View>

    </View>
  );
}


/* ============================================================
   EMPTY STATE
   ============================================================ */

export function EmptyState({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;

  title: string;

  description: string;
}) {

  return (
    <Card
      style={
        styles.emptyState
      }
    >

      <View
        style={
          styles.emptyIcon
        }
      >
        {icon}
      </View>


      <Text
        style={
          styles.emptyTitle
        }
      >
        {title}
      </Text>


      <Text
        style={
          styles.emptyDescription
        }
      >
        {description}
      </Text>

    </Card>
  );
}


/* ============================================================
   PLAN CARD
   ============================================================ */

export function PlanCard({
  plan,
  active,
  loading,
  onPress,
}: {
  plan: Plan;

  active: boolean;

  loading: boolean;

  onPress: () => void;
}) {

  const isFree =
    plan.id ===
    "free";


  return (
    <View
      style={[
        styles.planCard,

        active &&
          styles.planCardActive,
      ]}
    >

      <View
        style={
          styles.planHeader
        }
      >

        <View
          style={
            styles.planIcon
          }
        >

          {isFree ? (

            <Zap
              size={19}
              color={
                COLORS.primary
              }
            />

          ) : (

            <Crown
              size={19}
              color={
                COLORS.warning
              }
            />

          )}

        </View>


        <View
          style={
            styles.planInfo
          }
        >

          <View
            style={
              styles.planNameRow
            }
          >

            <Text
              style={
                styles.planName
              }
            >
              {plan.name}
            </Text>


            {active && (

              <View
                style={
                  styles.currentBadge
                }
              >

                <Text
                  style={
                    styles.currentBadgeText
                  }
                >
                  ACTUEL
                </Text>

              </View>

            )}

          </View>


          <Text
            style={
              styles.planDescription
            }
          >
            {plan.description}
          </Text>

        </View>


        <Text
          style={
            styles.planPrice
          }
        >
          {plan.price}
        </Text>

      </View>


      {!active && (

        <Pressable
          disabled={
            loading
          }
          onPress={
            onPress
          }
          style={[
            styles.planButton,

            loading &&
              styles.buttonDisabled,
          ]}
        >

          {loading ? (

            <ActivityIndicator
              size="small"
              color={
                COLORS.primary
              }
            />

          ) : (

            <Text
              style={
                styles.planButtonText
              }
            >
              {isFree
                ? "Choisir"
                : "S'abonner"}
            </Text>

          )}

        </Pressable>

      )}

    </View>
  );
}


/* ============================================================
   BOTTOM NAVIGATION
   ============================================================ */

export function BottomNavigation({
  activeScreen,
  onChange,
}: {
  activeScreen:
    Screen;

  onChange: (
    screen: Screen
  ) => void;
}) {

  const items: {
    id: Screen;

    label: string;

    icon: React.ReactNode;
  }[] = [

    {
      id: "help",
      label: "Help Me",
      icon: (
        <Lightbulb
          size={21}
        />
      ),
    },

    {
      id: "learn",
      label: "Learn",
      icon: (
        <BookOpen
          size={21}
        />
      ),
    },

    {
      id: "history",
      label: "Historique",
      icon: (
        <History
          size={21}
        />
      ),
    },

    {
      id: "profile",
      label: "Profil",
      icon: (
        <User
          size={21}
        />
      ),
    },

  ];


  return (
    <View
      style={
        styles.bottomNavigation
      }
    >

      {items.map(
        item => {

          const active =
            item.id ===
            activeScreen;


          return (
            <Pressable
              key={
                item.id
              }
              onPress={() =>
                onChange(
                  item.id
                )
              }
              style={
                styles.navItem
              }
            >

              <View
                style={[
                  styles.navIcon,

                  active &&
                    styles.navIconActive,
                ]}
              >

                {React.cloneElement(
                  item.icon as React.ReactElement,
                  {
                    color:
                      active
                        ? COLORS.primary
                        : COLORS.muted,
                  }
                )}

              </View>


              <Text
                style={[
                  styles.navLabel,

                  active &&
                    styles.navLabelActive,
                ]}
              >
                {item.label}
              </Text>

            </Pressable>
          );

        }
      )}

    </View>
  );
}


/* ============================================================
   ERROR MESSAGE
   ============================================================ */

export function ErrorMessage({
  message,
  onRetry,
}: {
  message: string;

  onRetry?: () => void;
}) {

  return (
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


      <View
        style={
          styles.errorContent
        }
      >

        <Text
          style={
            styles.errorText
          }
        >
          {message}
        </Text>


        {onRetry && (

          <Pressable
            onPress={
              onRetry
            }
          >

            <Text
              style={
                styles.retryText
              }
            >
              Réessayer
            </Text>

          </Pressable>

        )}

      </View>

    </View>
  );
}


/* ============================================================
   CREDIT BADGE
   ============================================================ */

export function CreditBadge({
  credits,
}: {
  credits: number;
}) {

  return (
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
        {credits}
      </Text>

    </View>
  );
}


/* ============================================================
   STREAMING INDICATOR
   ============================================================ */

export function StreamingIndicator() {

  return (
    <View
      style={
        styles.streamingIndicator
      }
    >

      <View
        style={
          styles.streamingIcon
        }
      >

        <Sparkles
          size={16}
          color={
            COLORS.primary
          }
        />

      </View>


      <Text
        style={
          styles.streamingText
        }
      >
        HintAI écrit...
      </Text>


      <View
        style={
          styles.streamingDots
        }
      >

        <View
          style={
            styles.typingDot
          }
        />

        <View
          style={
            styles.typingDot
          }
        />

        <View
          style={
            styles.typingDot
          }
        />

      </View>

    </View>
  );
}
```
