workspace "CDEK Delivery Service" "Архитектура сервиса доставки посылок (учебный пример)" {

    !identifiers hierarchical

    model {

        // ---------- Пользователи (роли) ----------
        sender = person "Клиент (отправитель)" "Регистрируется, создаёт посылки и доставки"
        recipient = person "Получатель" "Получает посылки, отслеживает статус доставки"

        // ---------- Внешние системы ----------
        paymentSystem = softwareSystem "Платёжный шлюз" "Внешняя платёжная система (ЮKassa)" {
            tags "External"
        }
        smsSystem = softwareSystem "SMS-сервис" "Внешний провайдер SMS-уведомлений" {
            tags "External"
        }
        emailSystem = softwareSystem "Email-сервис" "Внешний провайдер email-рассылки (SMTP/SendGrid)" {
            tags "External"
        }
        mapsSystem = softwareSystem "Сервис геокодирования" "Yandex Maps / 2GIS — расчёт адресов и расстояний" {
            tags "External"
        }

        // ---------- Наша система ----------
        cdek = softwareSystem "CDEK Service" "Сервис доставки посылок между пользователями" {

            webApp = container "Web Application" "SPA для клиентов: формы регистрации, посылок и доставок" "React / TypeScript"
            mobileApp = container "Mobile Application" "Мобильное приложение клиента" "iOS / Android"

            apiGateway = container "API Gateway" "Точка входа для клиентов, аутентификация, маршрутизация" "Go / Kong"

            userService = container "User Service" "Управление пользователями: создание, поиск по логину и по маске ФИО" "Go"
            parcelService = container "Parcel Service" "Управление посылками: создание, получение списка посылок пользователя" "Go"
            deliveryService = container "Delivery Service" "Управление доставками: создание, поиск по отправителю/получателю" "Go"
            notificationService = container "Notification Service" "Отправка уведомлений по событиям доставки" "Python / FastAPI"

            database = container "Relational Database" "Хранение пользователей, посылок и доставок" "PostgreSQL" {
                tags "Database"
            }
            cache = container "Cache" "Кеш для поиска пользователей" "Redis" {
                tags "Database"
            }
            broker = container "Message Broker" "Асинхронные события (DeliveryCreated, ParcelCreated)" "Apache Kafka" {
                tags "Queue"
            }

            // ---------- Связи внутри системы ----------
            webApp -> apiGateway "Вызывает API" "JSON/HTTPS"
            mobileApp -> apiGateway "Вызывает API" "JSON/HTTPS"

            apiGateway -> userService "Маршрутизирует запросы пользователей" "gRPC"
            apiGateway -> parcelService "Маршрутизирует запросы посылок" "gRPC"
            apiGateway -> deliveryService "Маршрутизирует запросы доставок" "gRPC"

            userService -> database "Читает/пишет пользователей" "JDBC/SQL"
            userService -> cache "Кеширует поиск по логину/ФИО" "RESP"

            parcelService -> database "Читает/пишет посылки" "JDBC/SQL"
            parcelService -> broker "Публикует событие ParcelCreated" "Kafka protocol"

            deliveryService -> database "Читает/пишет доставки" "JDBC/SQL"
            deliveryService -> userService "Проверяет существование получателя/отправителя" "gRPC"
            deliveryService -> parcelService "Получает данные посылки" "gRPC"
            deliveryService -> broker "Публикует событие DeliveryCreated" "Kafka protocol"

            notificationService -> broker "Подписан на события" "Kafka protocol"
        }

        // ---------- Связи пользователей с системой ----------
        sender -> cdek.webApp "Создаёт посылки и доставки" "HTTPS"
        sender -> cdek.mobileApp "Создаёт посылки и доставки" "HTTPS"
        recipient -> cdek.webApp "Отслеживает доставки" "HTTPS"
        recipient -> cdek.mobileApp "Отслеживает доставки" "HTTPS"

        // ---------- Связи с внешними системами ----------
        cdek.apiGateway -> paymentSystem "Проводит оплату доставки" "HTTPS/REST"
        cdek.notificationService -> smsSystem "Отправляет SMS" "HTTPS/REST"
        cdek.notificationService -> emailSystem "Отправляет email" "SMTP/HTTPS"
        cdek.deliveryService -> mapsSystem "Геокодирует адреса, считает маршрут" "HTTPS/REST"

        smsSystem -> recipient "Доставляет SMS-уведомление"
        emailSystem -> recipient "Доставляет email-уведомление"
        smsSystem -> sender "Доставляет SMS-уведомление"
        emailSystem -> sender "Доставляет email-уведомление"
    }

    views {

        // ---------- C1: System Context ----------
        systemContext cdek "C1_Context" "Контекст сервиса доставки" {
            include *
            autoLayout lr
        }

        // ---------- C2: Containers ----------
        container cdek "C2_Containers" "Контейнерная диаграмма CDEK Service" {
            include *
            autoLayout lr
        }

        // ---------- Dynamic: создание доставки ----------
        dynamic cdek "CreateDelivery" "Сценарий: отправитель создаёт доставку получателю" {
            sender -> cdek.webApp "Заполняет форму создания доставки"
            cdek.webApp -> cdek.apiGateway "POST /deliveries"
            cdek.apiGateway -> cdek.deliveryService "createDelivery(senderId, recipientLogin, parcelId)"
            cdek.deliveryService -> cdek.userService "Проверяет получателя по логину"
            cdek.userService -> cdek.cache "Ищет в кеше"
            cdek.userService -> cdek.database "SELECT user by login (если нет в кеше)"
            cdek.deliveryService -> cdek.parcelService "Получает данные посылки"
            cdek.parcelService -> cdek.database "SELECT parcel by id"
            cdek.deliveryService -> mapsSystem "Считает маршрут и стоимость"
            cdek.deliveryService -> cdek.database "INSERT delivery"
            cdek.deliveryService -> cdek.broker "Публикует DeliveryCreated"
            cdek.notificationService -> cdek.broker "Получает событие DeliveryCreated"
            cdek.notificationService -> smsSystem "Отправляет SMS получателю"
            cdek.notificationService -> emailSystem "Отправляет email получателю"
            cdek.deliveryService -> cdek.apiGateway "201 Created (deliveryId)"
            cdek.apiGateway -> cdek.webApp "HTTP 201 + JSON"
            cdek.webApp -> sender "Показывает подтверждение"
            autoLayout lr
        }

        theme default
    }
}