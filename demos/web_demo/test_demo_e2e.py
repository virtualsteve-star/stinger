            # Check for key elements that should be in the React app
            # Note: "chat" text is loaded by JavaScript, so check for static elements
            required_elements = [
                "Stinger",
                "textarea",
                "div id=\"root\"",
                "bundle.js"
            ]
            
            for element in required_elements:
                if element.lower() not in html.lower():
                    self.log(f"Frontend missing expected element: {element}", "ERROR")
                    return False
            
            return True 