#   [BlueprintWebSocket](https://www.unrealengine.com/marketplace/en-US/product/blueprintwebsocket) - Documentation 
|Table of content|
|:---:|
|[Blueprints](#blueprints)|
|[C++](#c)|
|[Support](#support)|

## Blueprints
### Asynchronous helper nodes
Coming soon...
### Full Blueprints
Coming soon...
## C++
### Include
BlueprintWebSocket requires you to include only one file:
```cpp
#include "BlueprintWebSocketWrapper.h"
```
### Creating a new WebSocket 
BlueprintWebSocket provides an easy way to create a socket:
```cpp
UBlueprintWebSocket* const WebSocket = UBlueprintWebSocket::CreateWebSocket();
```
### Configuring the WebSocket
Now that the WebSocket is created, we can configure it to talk with our WebSocket server.
Here is an exhaustive list of functions available for modifying the headers sent during the connection:
 ```cpp
// Merge the provided map with the current header list.
WebSocket->SetHeaders(const TMap<FString, FString> & InHeaders);

// Add a pair Key / Value to the list of headers.
WebSocket->AddHeader(const FString & Header, const FString & Value);

// Remove the header from the header list
WebSocket->RemoveHeader(const FString & HeaderToRemove);
```
### Listening to events with Callbacks
As the WebSocket is asynchronous, we need to listen to events to react to connection, connection error or messages.
Here is a list of the events and their signature:
|Event Name|Signature|Description|
|:---|:--|:--|
|`OnConnectedEvent`| `void Func()`|Called when we are successfully connected to the WebSocket Server.
|`OnConnectionErrorEvent`| `void Func(const FString & Error)`|Called when we failed to connect to the WebSocket server.
|`OnCloseEvent`| `void Func(int64 StatusCode, const FString & Reason, bool bWasClean)`|Called when the connection with the server has been closed.
|`OnMessageEvent`|`void Func(const FString & Message)`| Called when we received a string message.
|`OnRawMessageEvent`|`void Func(const TArray<uint8> & Data, int32 BytesRemaining)`|Called when we received a binary message.
|`OnMessageSentEvent`|`void Func(const FString & Message)`|Called just after we sent a message.

The WebSocket events are `Dynamic Multicast Delegates`, it requires the function bound to be declared as `UFUNCTION()`:
```cpp
UCLASS()
class MYGAME_API UMyClass : public UObject
{
    GENERATED_BODY()
public:
    // The function we use to bind the events
    void BindEvents();
private:
	// Callbacks
    UFUNCTION() void OnConnected();
    UFUNCTION() void OnConnectionError(const FString & Error);
    UFUNCTION() void OnClosed(int64 StatusCode, const FString & Reason, bool bWasClean);
    UFUNCTION() void OnMessage(const FString & Message);
    UFUNCTION() void OnRawMessage(const TArray<uint8> & Data, int32 BytesRemaining);
    UFUNCTION() void OnMessageSent(const FString & Message);
private:
    UPROPERTY()
    UBlueprintWebSocket* WebSocket;
};

void UMyClass::BindEvents()
{
    // Bind the events so our functions are called when the event is triggered.
    WebSocket->OnConnectedEvent      .AddDynamic(this, &UMyClass::OnConnected);
    WebSocket->OnConnectionErrorEvent.AddDynamic(this, &UMyClass::OnConnectionError);
    WebSocket->OnClosedEvent         .AddDynamic(this, &UMyClass::OnClosed);
    WebSocket->OnMessageEvent        .AddDynamic(this, &UMyClass::OnMessage);
    WebSocket->OnRawMessageEvent     .AddDynamic(this, &UMyClass::OnRawMessage);
    WebSocket->OnMessageSentEvent    .AddDynamic(this, &UMyClass::OnMessageSent);
}
```
|:warning:|It is recommended to bind all events you will use before connecting.|
|:---:|:---|

### Connecting to the WebSocket Server
To establish the connection with your WebSocket server, you have to call  `void Connect(const FString & Url, const FString & Protocol)`:
```cpp
WebSocket->Connect(TEXT("ws://myserver.com:8080/"), TEXT("ws"));
```
You can then check at any moment if you are connected with `bool IsConnected() const`:
```cpp
if (WebSocket->IsConnected())
{
    // We are connected.
}
else
{
    // We are not connected.
}
```
|:warning:|You shouldn't rely on `IsConnected()` to handle connection but on the `OnConnectedEvent` callback.|
|:---:|:---|
### Sending Messages
To send messages to your server, you have two possibilities:
1. `void SendMessage(const FString & Message)` 
To send String messages.
2. `void SendRawMessage(const TArray<uint8> & Message, const bool bIsBinary)` 
To send raw (binary) messages.

Their use is pretty similar:
```cpp
// The data we want to send, you can get it programmatically.
const FString       StringMessage = TEXT("Hello Server");
const TArray<uint8> BinaryMessage = { 0, 1, 2, 3, 4, 5 };

// Send it through our WebSocket.
WebSocket->SendMessage   (StringMessage);
WebSocket->SendRawMessage(BinaryMessage);
```

### Full Example
##### MyClass.h
```cpp
#pragma once

#include "CoreMinimal"
#include "MyClass.generated.h"

// Forward declaration. You can as well just include
// BlueprintWebSocketWrapper.h before MyClass.generated.h.
class UBlueprintWebSocket;

/**
 *  Our custom class that use a WebSocket.
 **/
UCLASS()
class MYGAME_API UMyClass : public UObject
{
    GENERATED_BODY()
public:
    // The function we use to create and connect our socket
    // to the WebSocket server.
    void InitializeAndConnectSocket();
private:
	// Callbacks
    UFUNCTION() void OnConnected();
    UFUNCTION() void OnConnectionError(const FString & Error);
    UFUNCTION() void OnClosed(int64 StatusCode, const FString & Reason, bool bWasClean);
    UFUNCTION() void OnMessage(const FString & Message);
    UFUNCTION() void OnRawMessage(const TArray<uint8> & Data, int32 BytesRemaining);
    UFUNCTION() void OnMessageSent(const FString & Message);
private:
    // The WebSocket, marking it as UPROPERTY prenvents it 
    // from being garbage collected as actions are latent.
    UPROPERTY()
    UBlueprintWebSocket* WebSocket;
};
```
#### MyClass.cpp
```cpp
#include "MyClass.h"
#include "BlueprintWebSocketWrapper.h"

void UMyClass::InitializeAndConnectSocket()
{
    // Create our new BlueprintWebsocket object.
    WebSocket = UBlueprintWebSocket::CreateWebSocket();
    
    // Bind the events so our functions are called when the events are triggered.
    WebSocket->OnConnectedEvent      .AddDynamic(this, &UMyClass::OnConnected);
    WebSocket->OnConnectionErrorEvent.AddDynamic(this, &UMyClass::OnConnectionError);
    WebSocket->OnClosedEvent         .AddDynamic(this, &UMyClass::OnClosed);
    WebSocket->OnMessageEvent        .AddDynamic(this, &UMyClass::OnMessage);
    WebSocket->OnRawMessageEvent     .AddDynamic(this, &UMyClass::OnRawMessage);
    WebSocket->OnMessageSentEvent    .AddDynamic(this, &UMyClass::OnMessageSent);

    // Add our headers.
    WebSocket->AddHeader(TEXT("SomeHeader"), TEXT("SomeValue"));

    // And we connect.
    WebSocket->Connect(TEXT("ws://localhost:8080/"), TEXT("ws"));
}

void UMyClass::OnConnected()
{
    // We successfully connected.
    UE_LOG(LogTemp, Log, TEXT("We are connected!"));
    
    // It's safe here to send some data to our server.
    WebSocket->SendMessage(TEXT("Hello Server!"));
}

void UMyClass::OnConnectionError(const FString & Error)
{
    // Connection failed.
    UE_LOG(LogTemp, Error, TEXT("Failed to connect: %s."), *Error);
}

void UMyClass::OnClosed(int64 StatusCode, const FString & Reason, bool bWasClean)
{
    // The connection has been closed.
    UE_LOG(LogTemp, Warning, TEXT("Connection closed: %d:%s. Clean: %d"), StatusCode, *Reason, bWasClean);
}

void UMyClass::OnMessage(const FString & Message)
{
    // The server sent us a message
    UE_LOG(LogTemp, Log, TEXT("New message: %s"), *Message);
}

void UMyClass::OnRawMessage(const TArray<uint8> & Data, int32 BytesRemaining)
{
    // We received a binary message.
    UE_LOG(LogTemp, Log, TEXT("New binary message: %d bytes and %d bytes remaining."), Data.Num(), BytesRemaining);
}

void UMyClass::OnMessageSent(const FString & Message)
{
    // We just sent a message
    UE_LOG(LogTemp, Log, TEXT("We just sent %s to the server."), *Message);
}
```

## Support
If you need help, have a feature request or experience troubles, please contact us at [pandores.marketplace@gmail.com](mailto:pandores.marketplace+BlueprintWebSocket@gmail.com?subject=BlueprintWebSocket%20-%20).
