# DIGITUX - Virtual Store with Odoo

ERP implementation and customization project developed for the fictional company **Digitux**, a startup focused on selling technological products through eCommerce.

---

# Project Description

Digitux is a company specialized in online technology sales.  
Currently, the company faces several organizational issues caused by the use of poorly integrated systems and manual processes.

Main problems identified:

- Manual order management.
- Lack of synchronization between sales and inventory.
- Limited stock control.
- Difficulties tracking customers and sales.
- Shipping delays.
- Limited business analytics capabilities.

To solve these issues, an ERP system based on **Odoo** has been developed, integrating multiple interconnected business modules.

---

# Project Objective

The main objective of this project is to design and implement a functional ERP environment using Odoo, integrating real business modules to improve Digitux’s internal management.

The system integrates functionalities related to:

- Sales
- Inventory
- CRM
- Purchases
- eCommerce and Website

The entire project runs locally using Docker.

---

# Technologies Used

- Odoo 17 Community
- Docker
- Docker Compose
- Python
- XML
- PostgreSQL
- Linux
- Git and GitHub

---

# Development Environment

The project was developed using:

- IsardVDI virtual machines
- Docker containers
- Odoo running locally
- PostgreSQL database system

---

# Project Structure

```bash
Odoo---Digitux-Tienda-Virtual/
│
├── addons/
│   ├── digitux_sales/
│   ├── digitux_inventory/
│   ├── digitux_crm/
│   ├── digitux_purchase/
│   ├── digitux_ecommerce/
│   └── digitux_web/
│
├── docker-compose.yml
├── README.md
├── start.sh
├── start_windows.bat
├── reset.sh
├── update_module.sh
└── requirements.txt
```

---

# Developed Modules

## Sales Module

Responsible for managing:

- Orders
- Customers
- Invoicing
- Commercial management

Developed by:
- Joana

---

## Inventory Module

Responsible for:

- Stock control
- Warehouse management
- Product updates
- Preventing stock shortages

Developed by:
- Ariadna

---

## CRM Module

Responsible for:

- Customer management
- Sales tracking
- Opportunity management
- Contact organization

Developed by:
- César

---

## Purchase Module

Responsible for:

- Supplier management
- Purchase orders
- Product replenishment

Developed by:
- Christopher

---

## eCommerce and Website Module

Responsible for:

- Online store
- Website integration
- Product catalog
- User interface

Developed by:
- Raúl

---

# Custom Digitux Web Module

The project includes a fully customized module called `digitux_web`, focused on improving the customer experience and integrating ERP functionalities directly into the website.

Main implemented models:

- `digitux.pc.build`
- `digitux.pc.build.line`
- `digitux.rma.request`
- `digitux.price.alert`
- `digitux.stock.alert`

Integrated with standard Odoo models:

- `product.template`
- `product.product`
- `sale.order`
- `crm.lead`
- `purchase.order`
- `res.partner`
- `website`
- `portal`

---

# Implemented Website Features

## Public Routes

- `/digitux` → Main landing page.
- `/digitux/configurador` → PC configurator with automatic quotation and CRM opportunity creation.
- `/digitux/comparador` → Product comparison system.
- `/digitux/rma` → Public warranty and return form.
- `/digitux/envio` → GLS/DHL shipping estimator.
- `/my/digitux` → Customer portal for builds and RMA requests.

---

# Views and Interface

The module includes multiple Odoo views:

- Tree/List views
- Form views
- Kanban views
- Search views

It also extends the standard Odoo product form using XML inheritance to include custom Digitux technical specifications.

---

# Menus and Backend Actions

A custom backend menu called `Digitux` was implemented with multiple submenus:

- Operations
- Catalog
- Purchases
- CRM management
- Alerts and notifications

---

# Controllers and Portal

The project includes:

- Public web controllers
- Customer portal controllers
- Functional website forms
- CSRF token protection
- Integration between website and ERP backend

---

# Functional Business Logic

The system simulates a real technological online store environment including:

- Product stock management
- Sales workflows
- CRM integration
- Purchase management
- Shipping estimation
- Product comparison
- RMA and warranty requests
- Customer alerts
- Website and portal integration

---

# Project Installation

## 1. Clone the repository

```bash
git clone https://github.com/Ixf2/Odoo---Digitux-Tienda-Virtual.git
```

---

## 2. Enter the project directory

```bash
cd Odoo---Digitux-Tienda-Virtual
```

---

## 3. Recommended Startup

### Linux/macOS

```bash
./start.sh
```

### Windows

```bat
start_windows.bat
```

---

## 4. Access Odoo

Open your browser and go to:

```txt
http://localhost:8069
```

---

# Database Information

The default database name is:

```txt
digitux
```

If you want to reset the environment and start from scratch:

```bash
./reset.sh
./start.sh
```

---

# Useful Commands

## Update the custom module

```bash
./update_module.sh
```

## View Docker logs

```bash
docker compose logs -f odoo
```

## Force clean Docker environment

```bash
docker compose down -v
./start.sh
```

---

# Docker Configuration

Basic environment example:

```yaml
services:
  web:
    image: odoo:17.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - ./addons:/mnt/extra-addons

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
```

---

# Implemented Features

- Custom model creation.
- Odoo module integration.
- Website and ERP synchronization.
- Custom menus and actions.
- XML inherited views.
- Forms and list views.
- Product management.
- Customer management.
- Supplier management.
- CRM integration.
- Sales automation.
- Shipping estimation.
- Product comparison tools.
- Customer portal.
- Warranty and RMA system.
- Full ERP integration.

---

# Fixed Issue in Version v3

This version fixes the installation error:

```text
TypeError: Type of related field digitux.price.alert.current_price is inconsistent with product.product.lst_price
```

Cause of the issue:

In Odoo 17, the field `product.product.lst_price` is defined as a `Float`, while the custom field `current_price` had originally been declared as `Monetary`.

Solution implemented in v3:

- `current_price` changed to `Float`
- `target_price` remains `Monetary`

To avoid reusing corrupted databases from previous failed installations, it is recommended to run:

```bash
docker compose down -v
./start.sh
```

---

# Work Planning

## Day 1

- Project organization.
- Needs analysis.
- Task distribution.
- Module integration planning.

## Day 2

- Research on Odoo models.
- Technical testing with Docker.
- Environment configuration.
- Initial development of models and views.

---

# Responsibilities Distribution

| Member | Assigned Module |
|---|---|
| Raúl | eCommerce and Website |
| Ariadna | Inventory |
| César | CRM |
| Christopher | Purchases |
| Joana | Sales |

---

# Achieved Objectives

- Complete modular integration.
- Real ERP environment simulation.
- Partial business process automation.
- Collaborative development using Git and GitHub.
- Functional Docker implementation.
- Website and ERP integration.
- Customer portal implementation.
- Realistic eCommerce workflow simulation.

---

# Project Status

Academic project currently under development.

---

# Authors

- Joana
- Raúl
- Ariadna
- César
- Christopher

GitHub:
- Ixf2

---

# License

Educational project created for academic purposes.
