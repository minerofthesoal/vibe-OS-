import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: Screen.width
    height: Screen.height

    property string accentColor: config.AccentColor || "#89b4fa"
    property string fontFamily: config.FontFamily || "Inter"
    property int fontSize: parseInt(config.FontSize) || 13
    property int cornerRadius: parseInt(config.RoundCorners) || 16

    // Background with blur
    Image {
        id: backgroundImage
        anchors.fill: parent
        source: config.Background || ""
        fillMode: Image.PreserveAspectCrop
        smooth: true
        visible: false
    }

    FastBlur {
        anchors.fill: backgroundImage
        source: backgroundImage
        radius: parseInt(config.BlurRadius) || 40
    }

    // Dim overlay
    Rectangle {
        anchors.fill: parent
        color: "#000000"
        opacity: parseFloat(config.DimBackground) || 0.4
    }

    // Clock at top
    ColumnLayout {
        anchors.top: parent.top
        anchors.topMargin: 80
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 4

        Text {
            text: Qt.formatTime(new Date(), "hh:mm")
            font.family: root.fontFamily
            font.pixelSize: 72
            font.weight: Font.Light
            color: "#ffffff"
            Layout.alignment: Qt.AlignHCenter
        }

        Text {
            text: Qt.formatDate(new Date(), "dddd, MMMM d")
            font.family: root.fontFamily
            font.pixelSize: 20
            font.weight: Font.Normal
            color: "#bac2de"
            Layout.alignment: Qt.AlignHCenter
        }
    }

    // Timer to update clock
    Timer {
        interval: 30000
        running: true
        repeat: true
        onTriggered: {
            timeLabel.text = Qt.formatTime(new Date(), "hh:mm")
        }
    }

    // Login container
    Rectangle {
        id: loginBox
        anchors.centerIn: parent
        anchors.verticalCenterOffset: 40
        width: 340
        height: loginColumn.height + 60
        color: Qt.rgba(0.07, 0.07, 0.11, 0.75)
        radius: root.cornerRadius
        border.width: 1
        border.color: Qt.rgba(0.27, 0.28, 0.35, 0.5)

        ColumnLayout {
            id: loginColumn
            anchors.centerIn: parent
            width: parent.width - 60
            spacing: 16

            // User avatar placeholder
            Rectangle {
                Layout.alignment: Qt.AlignHCenter
                width: 80
                height: 80
                radius: 40
                color: Qt.rgba(0.54, 0.71, 0.98, 0.2)
                border.width: 2
                border.color: Qt.rgba(0.54, 0.71, 0.98, 0.5)

                Text {
                    anchors.centerIn: parent
                    text: "󰀄"
                    font.family: "JetBrainsMono Nerd Font"
                    font.pixelSize: 36
                    color: root.accentColor
                }
            }

            // Username field
            TextField {
                id: userField
                Layout.fillWidth: true
                height: 44
                placeholderText: "Username"
                text: userModel.lastUser
                font.family: root.fontFamily
                font.pixelSize: root.fontSize
                color: "#cdd6f4"
                horizontalAlignment: TextInput.AlignHCenter

                background: Rectangle {
                    radius: 12
                    color: Qt.rgba(0.12, 0.12, 0.18, 0.8)
                    border.width: userField.activeFocus ? 2 : 1
                    border.color: userField.activeFocus ? root.accentColor : Qt.rgba(0.27, 0.28, 0.35, 0.5)

                    Behavior on border.color {
                        ColorAnimation { duration: 200 }
                    }
                }

                Keys.onReturnPressed: passwordField.focus = true
            }

            // Password field
            TextField {
                id: passwordField
                Layout.fillWidth: true
                height: 44
                placeholderText: "Password"
                echoMode: TextInput.Password
                font.family: root.fontFamily
                font.pixelSize: root.fontSize
                color: "#cdd6f4"
                horizontalAlignment: TextInput.AlignHCenter

                background: Rectangle {
                    radius: 12
                    color: Qt.rgba(0.12, 0.12, 0.18, 0.8)
                    border.width: passwordField.activeFocus ? 2 : 1
                    border.color: passwordField.activeFocus ? root.accentColor : Qt.rgba(0.27, 0.28, 0.35, 0.5)

                    Behavior on border.color {
                        ColorAnimation { duration: 200 }
                    }
                }

                Keys.onReturnPressed: sddm.login(userField.text, passwordField.text, sessionModel.lastIndex)
            }

            // Login button
            Button {
                id: loginButton
                Layout.fillWidth: true
                height: 44
                text: "Sign In"
                font.family: root.fontFamily
                font.pixelSize: root.fontSize + 1
                font.weight: Font.DemiBold

                contentItem: Text {
                    text: loginButton.text
                    font: loginButton.font
                    color: "#11111b"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                background: Rectangle {
                    radius: 12
                    color: loginButton.pressed ? Qt.darker(root.accentColor, 1.2)
                         : loginButton.hovered ? Qt.lighter(root.accentColor, 1.1)
                         : root.accentColor

                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }

                onClicked: sddm.login(userField.text, passwordField.text, sessionModel.lastIndex)
            }

            // Error message
            Text {
                id: errorMessage
                Layout.fillWidth: true
                text: ""
                color: "#f38ba8"
                font.family: root.fontFamily
                font.pixelSize: 12
                horizontalAlignment: Text.AlignHCenter
                visible: text !== ""
            }
        }
    }

    // Session selector (bottom left)
    ComboBox {
        id: sessionSelector
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 20
        width: 200
        model: sessionModel
        currentIndex: sessionModel.lastIndex
        textRole: "name"
        font.family: root.fontFamily
        font.pixelSize: 12

        background: Rectangle {
            radius: 10
            color: Qt.rgba(0.07, 0.07, 0.11, 0.7)
            border.width: 1
            border.color: Qt.rgba(0.27, 0.28, 0.35, 0.5)
        }

        contentItem: Text {
            text: sessionSelector.displayText
            color: "#a6adc8"
            font: sessionSelector.font
            leftPadding: 12
            verticalAlignment: Text.AlignVCenter
        }
    }

    // Power buttons (bottom right)
    Row {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 20
        spacing: 12

        Repeater {
            model: [
                { icon: "⏻", action: function() { sddm.powerOff() } },
                { icon: "⟳", action: function() { sddm.reboot() } },
                { icon: "⏾", action: function() { sddm.suspend() } }
            ]

            delegate: Rectangle {
                width: 40
                height: 40
                radius: 10
                color: powerMouse.containsMouse ? Qt.rgba(0.27, 0.28, 0.35, 0.6) : Qt.rgba(0.07, 0.07, 0.11, 0.5)
                border.width: 1
                border.color: Qt.rgba(0.27, 0.28, 0.35, 0.3)

                Behavior on color {
                    ColorAnimation { duration: 150 }
                }

                Text {
                    anchors.centerIn: parent
                    text: modelData.icon
                    font.pixelSize: 16
                    color: "#a6adc8"
                }

                MouseArea {
                    id: powerMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: modelData.action()
                }
            }
        }
    }

    // Handle login failure
    Connections {
        target: sddm
        function onLoginFailed() {
            errorMessage.text = "Login failed. Please try again."
            passwordField.text = ""
            passwordField.focus = true
        }
        function onLoginSucceeded() {
            errorMessage.text = ""
        }
    }

    // Focus password field on start
    Component.onCompleted: {
        if (userField.text !== "") {
            passwordField.focus = true
        } else {
            userField.focus = true
        }
    }
}
