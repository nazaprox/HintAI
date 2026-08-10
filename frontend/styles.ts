```ts
/**
 * HintAI
 * frontend/styles.ts
 *
 * Styles centralisés du frontend React Native.
 */

import {
  StyleSheet,
  Platform,
} from "react-native";


/* ============================================================
   COLORS
   ============================================================ */

export const COLORS = {
  primary: "#7C3AED",
  primaryLight: "#A78BFA",
  primaryDark: "#5B21B6",

  secondary: "#06B6D4",

  background: "#080B14",
  surface: "#111625",
  surfaceLight: "#171D30",
  surfaceLighter: "#20283D",

  text: "#F8FAFC",
  textSecondary: "#A8B2C5",
  muted: "#69748A",

  border: "#252D42",

  success: "#22C55E",
  error: "#EF4444",
  warning: "#F59E0B",

  white: "#FFFFFF",
  black: "#000000",

  transparent: "transparent",
};


/* ============================================================
   GLOBAL STYLES
   ============================================================ */

export const styles = StyleSheet.create({

  /* ----------------------------------------------------------
     APP
     ---------------------------------------------------------- */

  app: {
    flex: 1,
    backgroundColor:
      COLORS.background,
  },

  screen: {
    flex: 1,
    backgroundColor:
      COLORS.background,
  },

  content: {
    flexGrow: 1,
    paddingHorizontal: 18,
    paddingTop: 18,
    paddingBottom: 120,
  },


  /* ----------------------------------------------------------
     HEADER
     ---------------------------------------------------------- */

  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",

    paddingHorizontal: 18,
    paddingTop:
      Platform.OS === "ios"
        ? 12
        : 18,

    paddingBottom: 12,

    backgroundColor:
      COLORS.background,
  },

  headerLeft: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },

  logo: {
    width: 42,
    height: 42,

    borderRadius: 14,

    alignItems: "center",
    justifyContent: "center",

    backgroundColor:
      COLORS.primary,
  },

  logoText: {
    color:
      COLORS.white,

    fontSize: 20,
    fontWeight: "900",
  },

  headerTitle: {
    color:
      COLORS.text,

    fontSize: 20,
    fontWeight: "800",
  },

  headerSubtitle: {
    color:
      COLORS.textSecondary,

    fontSize: 12,

    marginTop: 2,
  },


  /* ----------------------------------------------------------
     BUTTONS
     ---------------------------------------------------------- */

  button: {
    minHeight: 52,

    paddingHorizontal: 18,

    borderRadius: 15,

    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",

    gap: 9,
  },

  buttonPrimary: {
    backgroundColor:
      COLORS.primary,
  },

  buttonSecondary: {
    backgroundColor:
      COLORS.surfaceLight,

    borderWidth: 1,

    borderColor:
      COLORS.border,
  },

  buttonDanger: {
    backgroundColor:
      COLORS.error,
  },

  buttonGhost: {
    backgroundColor:
      COLORS.transparent,
  },

  buttonPressed: {
    opacity: 0.78,

    transform: [
      {
        scale: 0.98,
      },
    ],
  },

  buttonDisabled: {
    opacity: 0.45,
  },

  buttonText: {
    color:
      COLORS.white,

    fontSize: 15,

    fontWeight: "800",
  },

  buttonTextSecondary: {
    color:
      COLORS.text,
  },

  buttonTextGhost: {
    color:
      COLORS.primaryLight,
  },


  /* ----------------------------------------------------------
     CARDS
     ---------------------------------------------------------- */

  card: {
    backgroundColor:
      COLORS.surface,

    borderRadius: 20,

    borderWidth: 1,

    borderColor:
      COLORS.border,

    padding: 17,

    marginBottom: 14,
  },


  /* ----------------------------------------------------------
     SOURCE SELECTOR
     ---------------------------------------------------------- */

  sourceSelector: {
    gap: 9,

    paddingVertical: 4,
  },

  sourceButton: {
    minHeight: 44,

    paddingHorizontal: 14,

    borderRadius: 13,

    borderWidth: 1,

    borderColor:
      COLORS.border,

    backgroundColor:
      COLORS.surface,

    flexDirection: "row",

    alignItems: "center",

    justifyContent: "center",

    gap: 7,
  },

  sourceButtonActive: {
    backgroundColor:
      COLORS.primary,

    borderColor:
      COLORS.primary,
  },

  sourceButtonText: {
    color:
      COLORS.textSecondary,

    fontSize: 13,

    fontWeight: "700",
  },

  sourceButtonTextActive: {
    color:
      COLORS.white,
  },


  /* ----------------------------------------------------------
     QUALITY
     ---------------------------------------------------------- */

  qualityBadge: {
    flexDirection: "row",

    alignItems: "center",

    borderRadius: 15,

    padding: 13,

    marginTop: 12,

    borderWidth: 1,
  },

  qualitySuccess: {
    backgroundColor:
      "rgba(34,197,94,0.08)",

    borderColor:
      "rgba(34,197,94,0.25)",
  },

  qualityError: {
    backgroundColor:
      "rgba(239,68,68,0.08)",

    borderColor:
      "rgba(239,68,68,0.25)",
  },

  qualityContent: {
    flex: 1,

    marginLeft: 10,
  },

  qualityTitle: {
    color:
      COLORS.text,

    fontSize: 13,

    fontWeight: "800",
  },

  qualityMessage: {
    color:
      COLORS.textSecondary,

    fontSize: 12,

    lineHeight: 17,

    marginTop: 2,
  },

  qualityScore: {
    color:
      COLORS.success,

    fontSize: 14,

    fontWeight: "900",
  },


  /* ----------------------------------------------------------
     LOADING
     ---------------------------------------------------------- */

  loadingBox: {
    alignItems: "center",

    justifyContent: "center",

    paddingVertical: 35,

    paddingHorizontal: 20,

    backgroundColor:
      COLORS.surface,

    borderRadius: 20,

    borderWidth: 1,

    borderColor:
      COLORS.border,
  },

  loadingIcon: {
    width: 55,
    height: 55,

    borderRadius: 18,

    alignItems: "center",
    justifyContent: "center",

    backgroundColor:
      "rgba(124,58,237,0.13)",

    marginBottom: 18,
  },

  loadingBoxTitle: {
    color:
      COLORS.text,

    fontSize: 17,

    fontWeight: "800",

    marginTop: 16,
  },

  loadingBoxDescription: {
    color:
      COLORS.textSecondary,

    fontSize: 13,

    textAlign: "center",

    lineHeight: 19,

    marginTop: 6,

    maxWidth: 300,
  },


  /* ----------------------------------------------------------
     MESSAGES
     ---------------------------------------------------------- */

  messageContainer: {
    width: "100%",

    alignItems: "flex-start",

    marginBottom: 12,
  },

  messageContainerUser: {
    alignItems: "flex-end",
  },

  messageBubble: {
    maxWidth: "91%",

    borderRadius: 18,

    paddingHorizontal: 15,

    paddingVertical: 13,

    borderWidth: 1,
  },

  userBubble: {
    backgroundColor:
      "rgba(124,58,237,0.18)",

    borderColor:
      "rgba(124,58,237,0.32)",

    borderBottomRightRadius: 5,
  },

  assistantBubble: {
    backgroundColor:
      COLORS.surface,

    borderColor:
      COLORS.border,

    borderBottomLeftRadius: 5,
  },

  messageHeader: {
    flexDirection: "row",

    alignItems: "center",

    gap: 6,

    marginBottom: 7,
  },

  messageAuthor: {
    color:
      COLORS.textSecondary,

    fontSize: 11,

    fontWeight: "800",
  },

  messageText: {
    color:
      COLORS.text,

    fontSize: 14,

    lineHeight: 21,
  },

  typingIndicator: {
    flexDirection: "row",

    alignItems: "center",

    gap: 5,

    paddingVertical: 4,
  },

  typingDot: {
    width: 6,
    height: 6,

    borderRadius: 3,

    backgroundColor:
      COLORS.primaryLight,
  },


  /* ----------------------------------------------------------
     EXERCISES
     ---------------------------------------------------------- */

  exerciseCard: {
    backgroundColor:
      COLORS.surface,

    borderRadius: 20,

    borderWidth: 1,

    borderColor:
      COLORS.border,

    padding: 17,

    marginBottom: 14,
  },

  exerciseHeader: {
    flexDirection: "row",

    alignItems: "center",

    marginBottom: 15,
  },

  exerciseNumber: {
    width: 42,
    height: 42,

    borderRadius: 13,

    alignItems: "center",
    justifyContent: "center",

    backgroundColor:
      "rgba(124,58,237,0.14)",
  },

  exerciseNumberText: {
    color:
      COLORS.primaryLight,

    fontSize: 16,

    fontWeight: "900",
  },

  exerciseHeaderContent: {
    flex: 1,

    marginLeft: 11,
  },

  exerciseTitle: {
    color:
      COLORS.text,

    fontSize: 15,

    fontWeight: "800",
  },

  exerciseSubtitle: {
    color:
      COLORS.muted,

    fontSize: 11,

    marginTop: 3,
  },

  exerciseContent: {
    color:
      COLORS.text,

    fontSize: 14,

    lineHeight: 22,
  },

  exerciseFooter: {
    flexDirection: "row",

    alignItems: "center",

    gap: 7,

    marginTop: 16,

    paddingTop: 12,

    borderTopWidth: 1,

    borderTopColor:
      COLORS.border,
  },

  exerciseFooterText: {
    color:
      COLORS.textSecondary,

    fontSize: 11,
  },


  /* ----------------------------------------------------------
     EMPTY STATE
     ---------------------------------------------------------- */

  emptyState: {
    alignItems: "center",

    justifyContent: "center",

    paddingVertical: 35,

    paddingHorizontal: 20,
  },

  emptyIcon: {
    width: 58,
    height: 58,

    borderRadius: 18,

    alignItems: "center",
    justifyContent: "center",

    backgroundColor:
      "rgba(124,58,237,0.12)",

    marginBottom: 14,
  },

  emptyTitle: {
    color:
      COLORS.text,

    fontSize: 17,

    fontWeight: "800",

    textAlign: "center",
  },

  emptyDescription: {
    color:
      COLORS.textSecondary,

    fontSize: 13,

    lineHeight: 20,

    textAlign: "center",

    marginTop: 7,

    maxWidth: 320,
  },


  /* ----------------------------------------------------------
     PLANS
     ---------------------------------------------------------- */

  planCard: {
    backgroundColor:
      COLORS.surface,

    borderRadius: 20,

    borderWidth: 1,

    borderColor:
      COLORS.border,

    padding: 16,

    marginBottom: 12,
  },

  planCardActive: {
    borderColor:
      COLORS.primary,

    backgroundColor:
      "rgba(124,58,237,0.08)",
  },

  planHeader: {
    flexDirection: "row",

    alignItems: "center",
  },

  planIcon: {
    width: 42,
    height: 42,

    borderRadius: 13,

    alignItems: "center",
    justifyContent: "center",

    backgroundColor:
      COLORS.surfaceLight,
  },

  planInfo: {
    flex: 1,

    marginLeft: 11,
  },

  planNameRow: {
    flexDirection: "row",

    alignItems: "center",

    gap: 7,
  },

  planName: {
    color:
      COLORS.text,

    fontSize: 15,

    fontWeight: "900",
  },

  planDescription: {
    color:
      COLORS.textSecondary,

    fontSize: 11,

    marginTop: 3,
  },

  planPrice: {
    color:
      COLORS.text,

    fontSize: 16,

    fontWeight: "900",
  },

  currentBadge: {
    paddingHorizontal: 7,

    paddingVertical: 3,

    borderRadius: 6,

    backgroundColor:
      "rgba(34,197,94,0.13)",
  },

  currentBadgeText: {
    color:
      COLORS.success,

    fontSize: 8,

    fontWeight: "900",
  },

  planButton: {
    minHeight: 42,

    borderRadius: 12,

    marginTop: 14,

    alignItems: "center",
    justifyContent: "center",

    backgroundColor:
      COLORS.surfaceLight,

    borderWidth: 1,

    borderColor:
      COLORS.border,
  },

  planButtonText: {
    color:
      COLORS.primaryLight,

    fontSize: 13,

    fontWeight: "800",
  },


  /* ----------------------------------------------------------
     BOTTOM NAVIGATION
     ---------------------------------------------------------- */

  bottomNavigation: {
    position: "absolute",

    left: 10,
    right: 10,
    bottom: 10,

    height: 68,

    borderRadius: 22,

    backgroundColor:
      "rgba(17,22,37,0.97)",

    borderWidth: 1,

    borderColor:
      COLORS.border,

    flexDirection: "row",

    alignItems: "center",

    justifyContent: "space-around",

    paddingHorizontal: 5,

    ...Platform.select({
      web: {
        boxShadow:
          "0px 8px 30px rgba(0,0,0,0.35)",
      },

      default: {
        shadowColor:
          "#000000",

        shadowOffset: {
          width: 0,
          height: 6,
        },

        shadowOpacity:
          0.25,

        shadowRadius:
          16,

        elevation: 12,
      },
    }),
  },

  navItem: {
    flex: 1,

    height: 62,

    alignItems: "center",

    justifyContent: "center",
  },

  navIcon: {
    width: 38,
    height: 30,

    borderRadius: 12,

    alignItems: "center",
    justifyContent: "center",
  },

  navIconActive: {
    backgroundColor:
      "rgba(124,58,237,0.13)",
  },

  navLabel: {
    color:
      COLORS.muted,

    fontSize: 9,

    fontWeight: "700",

    marginTop: 2,
  },

  navLabelActive: {
    color:
      COLORS.primaryLight,
  },


  /* ----------------------------------------------------------
     ERRORS
     ---------------------------------------------------------- */

  errorBox: {
    flexDirection: "row",

    alignItems: "flex-start",

    padding: 14,

    borderRadius: 15,

    backgroundColor:
      "rgba(239,68,68,0.08)",

    borderWidth: 1,

    borderColor:
      "rgba(239,68,68,0.25)",

    marginBottom: 12,
  },

  errorContent: {
    flex: 1,

    marginLeft: 9,
  },

  errorText: {
    color:
      COLORS.text,

    fontSize: 13,

    lineHeight: 19,
  },

  retryText: {
    color:
      COLORS.primaryLight,

    fontSize: 12,

    fontWeight: "800",

    marginTop: 7,
  },


  /* ----------------------------------------------------------
     CREDITS
     ---------------------------------------------------------- */

  creditBadge: {
    flexDirection: "row",

    alignItems: "center",

    gap: 5,

    paddingHorizontal: 10,

    paddingVertical: 7,

    borderRadius: 12,

    backgroundColor:
      "rgba(245,158,11,0.10)",

    borderWidth: 1,

    borderColor:
      "rgba(245,158,11,0.22)",
  },

  creditValue: {
    color:
      COLORS.text,

    fontSize: 12,

    fontWeight: "900",
  },


  /* ----------------------------------------------------------
     STREAMING
     ---------------------------------------------------------- */

  streamingIndicator: {
    flexDirection: "row",

    alignItems: "center",

    paddingVertical: 8,

    paddingHorizontal: 4,
  },

  streamingIcon: {
    width: 29,
    height: 29,

    borderRadius: 10,

    alignItems: "center",
    justifyContent: "center",

    backgroundColor:
      "rgba(124,58,237,0.12)",
  },

  streamingText: {
    color:
      COLORS.textSecondary,

    fontSize: 12,

    fontWeight: "700",

    marginLeft: 8,
  },

  streamingDots: {
    flexDirection: "row",

    alignItems: "center",

    gap: 4,

    marginLeft: 7,
  },

});
```
