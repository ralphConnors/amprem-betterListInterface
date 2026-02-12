import sys, json, binascii, os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from api_client import ApiClient

with open("api_and_id.json", 'r') as f:
    api_and_id = json.load(f)

console = Console()

class BetterInterface(ApiClient):
    def modified_get_all_members(self, not_id_list):
        try:
            with open("member_ids.json", 'r') as f:
                data_ids = json.load(f)
            with open("member_names.json", 'r') as f:
                data_names = json.load(f)

            if not data_ids or not data_names:
                raise FileNotFoundError
        except (FileNotFoundError, json.JSONDecodeError):
            set_url = self.url_switch[0] + self.user_id
            self.response = self.load_request(set_url, self.payload, False, self.api, "GET")
            self.data = self.response.json()
            
            if not self.data:
                if not_id_list:
                    print("No members found.")
                return
            
            self.dump_members()

        if not_id_list:
            try:
                if not data_ids or not data_names:
                    console.print("[bold red]No members found.[/bold red]")
                    return

                members_table = Table(show_header=True, header_style="bold cyan", box=None)
                members_table.add_column("No.", style="yellow", width=5)
                members_table.add_column("Member Name:")
                members_table.add_column("ID", justify="right")

                for n, key in enumerate(data_ids):
                    id_m = data_ids[key]
                    f_member = data_names.get(key, "Unknown")
                    members_table.add_row(str(n + 1), f_member, str(id_m))
                console.print(Panel(members_table, title="[bold yellow]Members[/bold yellow]", border_style="blue"))
            except (FileNotFoundError, json.JSONDecodeError):
                console.print("[bold red]Error: Could not read member data for display.[/bold red]")
    
    def modified_get_custom_fronts(self, not_id_list):
        try:
            with open("cfront_ids.json", 'r') as f:
                data_ids = json.load(f)
            with open("cfront_members.json", 'r') as f:
                data_names = json.load(f)

            if not data_ids or not data_names:
                raise FileNotFoundError
        except (FileNotFoundError, json.JSONDecodeError):
            set_url = self.url_switch[3] + self.user_id
            self.response = self.load_request(set_url, self.payload, False, self.api, "GET")
            self.data = self.response.json()
            
            if not self.data:
                if not_id_list:
                    console.print("[bold red]No custom fronts found.[/bold red]")
                return
            
            self.dump_custom_fronts()

        if not_id_list:
            try:
                if not data_ids or not data_names:
                    console.print("[bold red]No custom fronts found.[/bold red]")
                    return

                fronts_table = Table(show_header=True, header_style="hot_pink", box=None)
                fronts_table.add_column("No.", style="green", width=5)
                fronts_table.add_column("Fronts:")
                fronts_table.add_column("ID", justify="right")

                for n, key in enumerate(data_ids):
                    id_m = data_ids[key]
                    f_member = data_names.get(key, "Unknown")
                    fronts_table.add_row(str(n + 1), f_member, str(id_m))
                console.print(Panel(fronts_table, title="[bold green]Custom Fronts[/bold green]", border_style="magenta"))
            except (FileNotFoundError, json.JSONDecodeError):
                console.print("[bold red]Error: Could not read fronts data for display.[/bold red]")
    
    def modified_add_front(self, switch):
        # make two tables first.
        # Members table:
        members_table = Table(show_header=True, header_style="bold cyan", box=None)
        members_table.add_column("No.", style="yellow", width=5)
        members_table.add_column("Member Name:")

        # Fronts table:
        fronts_table = Table(show_header=True, header_style="hot_pink", box=None)
        fronts_table.add_column("No.", style="green", width=5)
        fronts_table.add_column("Fronts:")

        # OPEN FILES
        with open("member_names.json", 'r') as f:
            member_names = json.load(f)

        with open("member_ids.json", 'r') as f:
            member_ids = json.load(f)

        with open("cfront_ids.json", 'r') as f:
            custom_front_ids = json.load(f)
        
        with open("cfront_members.json", 'r') as f:
            custom_fronts = json.load(f)
        
        # MAKE PANELS
        for n, member in enumerate(member_ids):
            part_member = member_names.get(member, "Unknown")
            members_table.add_row(str(int(n)+1), part_member)
        
        for n, cfront in enumerate(custom_front_ids):
            part_front = custom_fronts.get(cfront, "Unknown")
            fronts_table.add_row(str(len(member_names)+int(n)+1), part_front)

        console.print(Panel(members_table, title="[bold yellow]Members[/bold yellow]", border_style="blue"))
        console.print(Panel(fronts_table, title="[bold green]Custom Fronts[/bold green]", border_style="magenta"))
         # Generate Document ID
        random_bytes = os.urandom(12)
        docId = binascii.hexlify(random_bytes).decode('utf-8')

        # Input prompt for adding member:
        total_options = len(member_names) + len(custom_fronts)

        if switch:
            console.print(f"[green]Select member/front to switch for front (1-{total_options})[/green]\n")
        else:
            console.print(f"[green]Select member/front to add to front (1-{total_options})[/green]\n")

        console.print("[yellow]Or select 0 if you wish to exit.[/yellow]\n")

        try:
            selected_front = int((input(f">>> ")))
        except ValueError:
            console.print("[red]Invalid response.[/red]")
            return
        
        if selected_front == 0:
            console.print("[yellow]Request aborted.[/yellow]")
        elif selected_front > total_options:
            console.print("[red]Please try again.[/red]")
        else:
            # Determine if selection is member or custom front
            if selected_front <= len(member_names):
                selected_front_str = str(selected_front-1)
                fronter_to_add = {}
                fronter_to_add[docId] = member_ids[selected_front_str]
                front_value = member_ids[selected_front_str]
            else:
                custom_front_idx = str(selected_front - len(member_names) -1)
                fronter_to_add = {}
                fronter_to_add[docId] = custom_front_ids[custom_front_idx]
                front_value = custom_front_ids[custom_front_idx]

            # Add new member/front to fronting_members.json file
            try:
                with open("fronting_members.json", "r") as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {}
            
            if front_value in data.values():
                console.print("[yellow]Member/Front already in front, please remove if possible.[/yellow]")
            else:
                if switch:
                    self.remove_all_fronters()

                data.update(fronter_to_add)

                with open("fronting_members.json", "w") as f:
                    json.dump(data, f, indent=2)
                
                # Building the request
                set_url = self.url_switch[2] + docId
                self.payload = self.build_payload(True, True, self.get_current_epoch(), "start", front_value)
                self.load_request(set_url, self.payload, True, self.api, "POST")
                console.print("[green]Request successful.[/green]")


def apply_patch():
    if 'api_client' in sys.modules:
        client_module = sys.modules['api_client']

        if hasattr(client_module, 'ApiClient'):
            client_module.ApiClient.get_all_members = BetterInterface.modified_get_all_members
            client_module.ApiClient.get_custom_fronts = BetterInterface.modified_get_custom_fronts
            client_module.ApiClient.add_front = BetterInterface.modified_add_front

        else:
            console.print("[bold red]Plugin: Could not find ApiClient in api_client.py[/bold red]")
    else:
        print('Plugin: Could not find api_client.py')

def run():
    example_text = (
        "[yellow]Better List Interface 1.0[/yellow]\n\n"
        "Modifies interface for: \n- get_all_members\n- get_custom_fronts\n- add_front\n- switch_front"
    )

    console.print(Panel(example_text, title="[bold blue]EXAMPLE PLUGIN[/bold blue]", border_style="green"))

apply_patch()