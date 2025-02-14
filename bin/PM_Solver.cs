using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography.X509Certificates;
using Google.OrTools.Sat;

public class ParallelMachineScheduling
{
    private class AssignedTask //: IComparable
    {
        public int jobID;
        public int machineID;
        public int start;
        public int duration;

        public AssignedTask(int jobID, int machineID, int start, int duration)
        {
            this.jobID = jobID;
            this.machineID = machineID;
            this.start = start;
            this.duration = duration;
        }

        /*public int CompareTo(object obj)
        {
            if (obj == null)
                return 1;

            AssignedTask otherTask = obj as AssignedTask;
            if (otherTask != null)
            {
                if (this.start != otherTask.start)
                    return this.start.CompareTo(otherTask.start);
                else
                    return this.duration.CompareTo(otherTask.duration);
            }
            else
                throw new ArgumentException("Object is not a Task");
        }*/
    }

    public static void Main(String[] args)
    {
        var allJobs = new[] {
            new { duration = 3, earliestStart = 7, dueDate = 15, priority = 4 },
            new { duration = 8, earliestStart = 0, dueDate = 10, priority = 1 },
            new { duration = 1, earliestStart = 6, dueDate = 18, priority = 3 },
            new { duration = 5, earliestStart = 3, dueDate = 12, priority = 2 },
            new { duration = 7, earliestStart = 8, dueDate = 9, priority = 4 },
            new { duration = 4, earliestStart = 2, dueDate = 14, priority = 1 },
            new { duration = 6, earliestStart = 5, dueDate = 11, priority = 3 },
            new { duration = 2, earliestStart = 9, dueDate = 8, priority = 2 },
            new { duration = 9, earliestStart = 1, dueDate = 13, priority = 4 }
        };

        int numMachines = 6;
        int numJobs = allJobs.Length;

        // Computes horizon dynamically as the sum of all durations.
        int horizon = allJobs.Sum(job => job.duration);

        // Creates the model.
        CpModel model = new CpModel();

        // Variables for each job: start, end, machine, and interval.
        var allTasks = new Dictionary<int, (IntVar start, IntVar end, IntVar machine, IntervalVar interval)>();
        var machineToIntervals = new Dictionary<int, List<IntervalVar>>();
        List<IntVar> jobsTardiness = new List<IntVar>();

        for (int m = 0; m < numMachines; m++)
        {
            machineToIntervals[m] = new List<IntervalVar>();
        }

        for (int jobID = 0; jobID < numJobs; ++jobID)
        {
            var job = allJobs[jobID];

            // Variables for start, end, and machine assignment.
            IntVar start = model.NewIntVar(0, horizon, "start" + jobID);
            IntVar end = model.NewIntVar(0, horizon, "end" + jobID);
            IntVar machine = model.NewIntVar(0, numMachines - 1, "machine" + jobID);

            // Add constraint for earliest start time.
            model.Add(start >= job.earliestStart);

            IntVar tardiness = model.NewIntVar(0, horizon, $"tardiness_{jobID}");
            jobsTardiness.Add(tardiness);

            // Create optional intervals for each machine.
            for (int m = 0; m < numMachines; m++)
            {
                BoolVar isOnMachine = model.NewBoolVar($"isOnMachine_{jobID}_{m}");
                IntervalVar optionalInterval = model.NewOptionalIntervalVar(start, job.duration, end, isOnMachine, $"optionalInterval_{jobID}_{m}");

                machineToIntervals[m].Add(optionalInterval);

                // Link global interval to machine assignment.
                model.Add(machine == m).OnlyEnforceIf(isOnMachine);
                model.Add(machine != m).OnlyEnforceIf(isOnMachine.Not());
            }

            // Global interval variable.
            IntervalVar interval = model.NewIntervalVar(start, job.duration, end, "interval" + jobID);
            allTasks[jobID] = (start, end, machine, interval);
        }

        // Add disjunctive constraints for all intervals on each machine.
        foreach (var machineIntervals in machineToIntervals.Values)
        {
            model.AddNoOverlap(machineIntervals);
        }

        // Tardiness objective.
        for (int j = 0; j < numJobs; j++)
        {
            // Tardiness Constraints: Tardiness muss korrekt berechnet werden
            model.Add(jobsTardiness[j] >= allTasks[j].Item2 - allJobs[j].dueDate);
            model.Add(jobsTardiness[j] >= 0);
        }

        // Gewichtete Zielfunktion: Prioritätsgewichtung der Tardiness
        model.Minimize(LinearExpr.Sum(jobsTardiness.Select((tardiness, j) => tardiness * (5 - allJobs[j].priority))));


        // Solve.
        CpSolver solver = new CpSolver();
        CpSolverStatus status = solver.Solve(model);
        Console.WriteLine($"Solve status: {status}");
        Console.WriteLine($"Solution Sum of Weighted Tardiness: {solver.ObjectiveValue}");


        if (status == CpSolverStatus.Optimal || status == CpSolverStatus.Feasible)
        {
            Console.WriteLine("Solution:");
            Dictionary<int, List<AssignedTask>> assignedTasks = new Dictionary<int, List<AssignedTask>>();

            // Initialisiere Maschinen-Listen
            for (int m = 0; m < numMachines; m++)
            {
                assignedTasks[m] = new List<AssignedTask>();
            }

            // Aufgaben den Maschinen zuordnen
            foreach (var task in allTasks)
            {
                int jobID = task.Key;
                int start = (int)solver.Value(task.Value.start);
                int duration = allJobs[jobID].duration;
                int machineID = (int)solver.Value(task.Value.machine);

                assignedTasks[machineID].Add(new AssignedTask(jobID, machineID, start, duration));
            }

            // HTML-Datei für den Google Gantt Chart generieren
            using (StreamWriter writer = new StreamWriter("schedule.html"))
            {
                writer.WriteLine("<script type=\"text/javascript\" src=\"https://www.gstatic.com/charts/loader.js\"></script>");
                writer.WriteLine("<script type=\"text/javascript\">");
                writer.WriteLine("google.charts.load('current', {packages:['timeline']});");
                writer.WriteLine("google.charts.setOnLoadCallback(drawChart);");
                writer.WriteLine("function drawChart() {");
                writer.WriteLine("var data = new google.visualization.DataTable();");
                writer.WriteLine("data.addColumn( {type: 'string', id: 'Machinenumber'});");
                writer.WriteLine("data.addColumn( {type: 'string', id: 'Task'});");
                writer.WriteLine("data.addColumn( {type: 'date', id: 'Start Date'});");
                writer.WriteLine("data.addColumn( {type: 'date', id: 'End Date'});");
                writer.WriteLine("data.addRows([");

                // Aufgaben in die Tabelle schreiben
                foreach (int machineID in assignedTasks.Keys)
                {
                    foreach (var task in assignedTasks[machineID])
                    {
                        // Konvertiere Startzeit und Endzeit in Date-Format
                        int startHour = task.start; // Startzeit als Stunde (Vereinfachung)
                        int endHour = task.start + task.duration; // Endzeit berechnen
                        writer.WriteLine($"['Machine {task.machineID}', 'Job {task.jobID}', new Date(0, 0, 0, 0, 0, {startHour}), new Date(0, 0, 0, 0, 0, {endHour})],");
                    }
                }

                writer.WriteLine("]);");
                writer.WriteLine("var options = {height: 500};");
                writer.WriteLine("var chart = new google.visualization.Timeline(document.getElementById('chart_div'));");
                writer.WriteLine("chart.draw(data);");
                writer.WriteLine("}");
                writer.WriteLine("</script>");
                writer.WriteLine("</head>");
                writer.WriteLine("<body>");
                writer.WriteLine($"<div> <p>Tardiness: {solver.ObjectiveValue}</p> </div>");
                writer.WriteLine("<div id=\"chart_div\" style=\"width: 100%; height: 500px;\"></div>");
                writer.WriteLine("</body>");
            }

            Console.WriteLine("Schedule saved to 'schedule.html'");
        }
        else
        {
            Console.WriteLine("No solution found.");
        }
        try
        {
            var process = new System.Diagnostics.Process();
            process.StartInfo.FileName = "schedule.html";
            process.StartInfo.UseShellExecute = true; // Notwendig, um die Standardanwendung zu öffnen
            process.Start();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Failed to open the schedule file in the browser: {ex.Message}");
        }
    }
}